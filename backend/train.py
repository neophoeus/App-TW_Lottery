import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.predictor import LotteryPredictor, RULES
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.callbacks import EarlyStopping
except ImportError:
    print("TensorFlow not installed. Please install it to train LSTM.")
    sys.exit(1)

def build_and_train(game_key):
    print(f"=====================================")
    print(f"Preparing data for {game_key}...")
    predictor = LotteryPredictor(game_key)
    success, msg = predictor.load_data()
    if not success:
        print(f"Failed to load data for {game_key}: {msg}")
        return
        
    draws = predictor.draws
    max_n = predictor.max_num
    
    if len(draws) < 50:
        print(f"Not enough data for {game_key}, skipping. Need at least 50 draws.")
        return

    data_arr = []
    
    for d in draws:
        vec = np.zeros(max_n, dtype=np.float32)
        nums = d['nums']
        for n in nums:
            if 1 <= n <= max_n: vec[n-1] = 1.0
            
        s_ratio = sum(nums) / (max_n * predictor.game['z1_count'])
        odd_ratio = sum(1 for n in nums if n % 2 != 0) / predictor.game['z1_count']
        span_ratio = (max(nums) - min(nums)) / max_n if nums else 0
        
        aux = np.array([s_ratio, odd_ratio, span_ratio], dtype=np.float32)
        combined = np.concatenate([vec, aux])
        data_arr.append(combined)
        
    data_arr = np.array(data_arr[::-1])
    
    window_size = 20
    X, y = [], []
    for i in range(len(data_arr) - window_size):
        X.append(data_arr[i:i+window_size])
        y.append(data_arr[i+window_size][:max_n])
        
    X = np.array(X)
    y = np.array(y)
    
    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    
    input_dim = data_arr.shape[1]
    
    print(f"Training Model for {game_key} (X shape: {X.shape})...")
    
    model = keras.Sequential([
        layers.LSTM(128, return_sequences=True, input_shape=(window_size, input_dim)),
        layers.Dropout(0.3),
        layers.LSTM(64),
        layers.Dropout(0.3),
        layers.Dense(max_n, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy')
    
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32, callbacks=[early_stop], verbose=1)
    
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f'{game_key}_lstm.keras')
    model.save(model_path)
    print(f"Saved {game_key} model to {model_path}\n")

if __name__ == "__main__":
    for gk in RULES.keys():
        build_and_train(gk)
