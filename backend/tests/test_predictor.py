import sys
import os
import pytest

# Add backend directory to sys.path to resolve imports correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.predictor import LotteryPredictor, RULES

def test_rules_configuration():
    """Test that default rules configuration is valid."""
    assert "power" in RULES
    assert "big" in RULES
    assert "539" in RULES
    
    # Verify properties
    assert RULES["power"]["has_special"] is True
    assert RULES["big"]["has_special"] is False
    assert RULES["539"]["has_special"] is False

def test_predictor_initialization():
    """Test predictor initialization for all game types."""
    for game_key in RULES.keys():
        predictor = LotteryPredictor(game_key)
        assert predictor.game_key == game_key
        assert predictor.game == RULES[game_key]
        assert predictor.max_num == RULES[game_key]["z1_range"][1]

def test_predictor_load_data():
    """Test that predictor can load CSV data correctly."""
    for game_key in RULES.keys():
        predictor = LotteryPredictor(game_key)
        success, msg = predictor.load_data()
        assert success is True, f"Failed to load data for {game_key}: {msg}"
        assert len(predictor.draws) > 0, f"No draws loaded for {game_key}"
        
        # Verify first draw structure
        first_draw = predictor.draws[0]
        assert "date" in first_draw
        assert "nums" in first_draw
        assert "special" in first_draw
        assert len(first_draw["nums"]) == RULES[game_key]["z1_count"]

def test_predictor_strategies():
    """Test each individual strategy output for correct range and length."""
    for game_key in RULES.keys():
        predictor = LotteryPredictor(game_key)
        success, _ = predictor.load_data()
        assert success is True
        
        # Test Hot strategy
        hot_res = predictor.strategy_hot()
        assert len(hot_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in hot_res["nums"])
        if predictor.game["has_special"]:
            assert predictor.game["z2_range"][0] <= hot_res["special"] <= predictor.game["z2_range"][1]
            
        # Test Balanced strategy
        balanced_res = predictor.strategy_balanced()
        assert len(balanced_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in balanced_res["nums"])

        # Test Markov strategy
        markov_res = predictor.strategy_markov()
        assert len(markov_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in markov_res["nums"])

        # Test Pattern strategy
        pattern_res = predictor.strategy_pattern()
        assert len(pattern_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in pattern_res["nums"])

        # Test Gap strategy
        gap_res = predictor.strategy_gap()
        assert len(gap_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in gap_res["nums"])

        # Test Tail strategy
        tail_res = predictor.strategy_tail()
        assert len(tail_res["nums"]) == predictor.game["z1_count"]
        assert all(predictor.game["z1_range"][0] <= n <= predictor.game["z1_range"][1] for n in tail_res["nums"])

def test_predictor_run_all():
    """Test run_all outputs for correct keys and ensemble structure."""
    predictor = LotteryPredictor("power")
    predictor.load_data()
    results = predictor.run_all()
    
    assert "game" in results
    assert "last_date" in results
    assert "total_draws" in results
    assert "strategies" in results
    
    # Ensure strategies list contains the strategies and the final ensemble
    strategies = results["strategies"]
    assert len(strategies) >= 7 # At least 7 strategies (Hot, Balanced, Markov, Pattern, LSTM, Gap, Tail) + Ensemble
    
    # Check ensemble (last item)
    ensemble = strategies[-1]
    assert ensemble["name"] == "綜合預測"
    assert len(ensemble["nums"]) == RULES["power"]["z1_count"]

def test_model_caching_mechanism():
    """Test that Keras models are cached correctly and not reloaded repeatedly."""
    from unittest.mock import patch, MagicMock
    import core.predictor
    
    # Reset model cache
    core.predictor._MODEL_CACHE.clear()
    
    # Mock TensorFlow availability to True and mock load_model
    with patch("core.predictor.TF_AVAILABLE", True), \
         patch("core.predictor.keras.models.load_model") as mock_load_model, \
         patch("core.predictor.os.path.exists", return_value=True):
         
        # Create mock model that returns predictions
        import numpy as np
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.1] * 38])
        mock_load_model.return_value = mock_model
        
        predictor = LotteryPredictor("power")
        # Populate dummy draws for LSTM strategy (needs at least 20 draws)
        predictor.draws = [{"date": "2026-06-05", "nums": [1, 2, 3, 4, 5, 6], "special": 7} for _ in range(25)]
        
        # First call should call load_model
        res1 = predictor.strategy_lstm()
        assert "error" not in res1
        assert mock_load_model.call_count == 1
        assert "power" in core.predictor._MODEL_CACHE
        
        # Second call should use cached model and not call load_model again
        res2 = predictor.strategy_lstm()
        assert "error" not in res2
        assert mock_load_model.call_count == 1  # Still 1

