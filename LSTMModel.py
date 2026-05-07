import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os
import json

# === LIST: 50 STOCKS ===
STOCKS_TO_TRAIN = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC', 
    'JPM', 'V', 'WMT', 'KO', 'DIS', 'PEP', 'COST', 'MCD', 'NKE', 'CRM', 'UBER', 
    'PYPL', 'BA', 'IBM', 'SBUX',
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 'SBIN.NS', 
    'TATAMOTORS.NS', 'ITC.NS', 'WIPRO.NS', 'LT.NS', 'TATASTEEL.NS', 'SUNPHARMA.NS', 
    'BAJFINANCE.NS', 'MARUTI.NS', 'ZOMATO.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS', 
    'AXISBANK.NS', 'ASIANPAINT.NS', 'M&M.NS', 'TITAN.NS', 'NTPC.NS', 'ULTRACEMCO.NS', 
    'POWERGRID.NS', 'BHEL.NS'
]

def train_and_save_model(ticker):
    print(f"\n" + "="*50)
    print(f"🚀 STARTING TRAINING FOR: {ticker}")
    print("="*50)
    
    try:
        # 1. Data Download (5 Years for better accuracy)
        data = yf.download(ticker, period="5y", interval="1d")
        if data.empty:
            print(f"❌ No data found for {ticker}")
            return
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data[['Close']].dropna()
        dataset = df.values
        
        # 2. Scaling
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)
        
        # Save Scaler
        scaler_path = f"saved_models/{ticker}_scaler.pkl"
        joblib.dump(scaler, scaler_path)
        
        # 3. Prepare Training Data
        time_step = 60
        X_train, y_train = [], []
        for i in range(time_step, len(scaled_data)):
            X_train.append(scaled_data[i-time_step:i, 0])
            y_train.append(scaled_data[i, 0])
            
        X_train, y_train = np.array(X_train), np.array(y_train)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        
        # 4. Build Model (Anti-Overfitting Architecture)
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
        
        # 5. Smart Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss', 
            patience=10, 
            restore_best_weights=True,
            verbose=1
        )
        
        # 6. Training with Live Logging
        print(f"⏳ Training {ticker}... Monitoring Loss and MAE...")
        history = model.fit(
            X_train, y_train, 
            batch_size=32, 
            epochs=100, 
            validation_split=0.1, 
            callbacks=[early_stop], 
            verbose=1
        )
        
        # 7. Save Training History (JSON)
        if history is not None:
            history_path = f"saved_models/{ticker}_history.json"
            with open(history_path, 'w') as f:
                json.dump(history.history, f)
            print(f"📈 History Report Saved: {history_path}")
        
        # 8. Save Model
        model_path = f"saved_models/{ticker}_model.h5"
        model.save(model_path)
        
        # 9. Final Accuracy Check
        train_predict = model.predict(X_train, verbose=0)
        rmse = np.sqrt(mean_squared_error(y_train, train_predict))
        r2 = r2_score(y_train, train_predict)
        
        print(f"\n{ticker} TRAINING COMPLETE!")
        print(f"   ➤ RMSE: {rmse:.5f}")
        print(f"   ➤ R2 Score: {r2:.5f} (Target: Closer to 1.0)")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR training {ticker}: {str(e)}")

# Create folder if not exists
if not os.path.exists('saved_models'):
    os.makedirs('saved_models')

# Execute Training Loop
if __name__ == "__main__":
    print(f"Starting Bulk Training for {len(STOCKS_TO_TRAIN)} Stocks...")
    for stock in STOCKS_TO_TRAIN:
        train_and_save_model(stock)
    
    print("\n" + "X"*50)
    print("ALL MODELS TRAINED!")
    print("X"*50)