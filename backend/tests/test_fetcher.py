import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add backend directory to sys.path to resolve imports correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import LottoFetcher, GAMES

# Mock HTML sample page mimicking lotto-8.com structure
MOCK_HTML_BIG = """
<html>
  <body>
    <table>
      <tr>
        <td>2026/06/05</td>
        <td>05</td>
        <td>12</td>
        <td>18</td>
        <td>25</td>
        <td>36</td>
        <td>41</td>
        <td>09</td>
      </tr>
      <tr>
        <td>2026/06/04</td>
        <td>01</td>
        <td>02</td>
        <td>03</td>
        <td>04</td>
        <td>05</td>
        <td>06</td>
        <td>07</td>
      </tr>
    </table>
  </body>
</html>
"""

def test_games_configuration():
    """Verify that crawler target configurations exist."""
    assert "big" in GAMES
    assert "power" in GAMES
    assert "539" in GAMES
    
    assert GAMES["big"]["cols_count"] == 8
    assert GAMES["539"]["cols_count"] == 6

@patch("requests.get")
def test_fetch_game_success(mock_get, tmp_path):
    """Test successful HTML parsing and CSV export for fetch_game."""
    # Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = MOCK_HTML_BIG
    mock_get.return_value = mock_resp
    
    # Configure temporary CSV file to avoid writing to production data
    test_csv = tmp_path / "test_big.csv"
    
    # Use monkeypatch to temporarily redirect big.csv path
    with patch.dict(GAMES["big"], {"csv": str(test_csv)}):
        fetcher = LottoFetcher()
        success, msg = fetcher.fetch_game("big", max_pages=1)
        
        assert success is True
        assert "Updated" in msg
        assert os.path.exists(test_csv)
        
        # Read generated CSV and verify content
        import pandas as pd
        df = pd.read_csv(test_csv)
        assert len(df) == 2
        # Oldest first sorting
        assert df.iloc[0]["date"] == "2026-06-04"
        assert df.iloc[1]["date"] == "2026-06-05"
        
        # Verify columns and data format
        assert df.iloc[0]["n1"] == 1
        assert df.iloc[0]["special"] == 7

@patch("requests.get")
def test_fetch_all(mock_get, tmp_path):
    """Test fetch_all calls all three lottery fetches."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = MOCK_HTML_BIG
    mock_get.return_value = mock_resp
    
    test_big = tmp_path / "big.csv"
    test_power = tmp_path / "power.csv"
    test_539 = tmp_path / "539.csv"
    
    # Patch all game csv paths
    patched_games = {
        "big": {**GAMES["big"], "csv": str(test_big)},
        "power": {**GAMES["power"], "csv": str(test_power)},
        "539": {**GAMES["539"], "csv": str(test_539)}
    }
    
    with patch.dict(GAMES, patched_games):
        fetcher = LottoFetcher()
        results = fetcher.fetch_all()
        
        assert "big" in results
        assert "power" in results
        assert "539" in results
        
        # Verify files were created
        assert os.path.exists(test_big)
        assert os.path.exists(test_power)
        # Note: 539 expects 6 columns, HTML mock has 8. Fetcher will parse and adjust accordingly
        assert os.path.exists(test_539)
