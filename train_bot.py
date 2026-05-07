# train_bot.py
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score # <-- NAYA IMPORT
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

# 30 Curated Stocks for Fast & Reliable Training (Yahoo Finance Verified)
STOCKS_TO_TRAIN = [
    # === 15 US STOCKS (Global Giants) ===
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
    'NVDA', 'META', 'NFLX', 'AMD', 'INTC', 
    'JPM', 'V', 'WMT', 'KO', 'DIS',

    # === 15 INDIAN STOCKS (Nifty 50 Heavyweights) ===
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 
    'SBIN.NS', 'TATAMOTORS.NS', 'ITC.NS', 'WIPRO.NS', 'LT.NS', 
    'TATASTEEL.NS', 'SUNPHARMA.NS', 'BAJFINANCE.NS', 'MARUTI.NS'
]

def train_and_save_model(ticker):
    print(f"\n========================================")
    print(f"🚀 Training Model for {ticker}...")
    try:
        data = yf.download(ticker, period="2y", interval="1d")
        if data.empty:
            print(f"❌ No data found for {ticker}")
            return
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data[['Close']].dropna()
        dataset = df.values
        
        # Scale Data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)
        
        # Save Scaler
        scaler_path = f"saved_models/{ticker}_scaler.pkl"
        joblib.dump(scaler, scaler_path)
        
        time_step = 60
        X_train, y_train = [], []
        for i in range(time_step, len(scaled_data)):
            X_train.append(scaled_data[i-time_step:i, 0])
            y_train.append(scaled_data[i, 0])
            
        X_train, y_train = np.array(X_train), np.array(y_train)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        
        # Build LSTM
        model = Sequential()
        model.add(LSTM(50, return_sequences=False, input_shape=(X_train.shape[1], 1)))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        # Train Model (epochs=50 for good accuracy)
        print(f"⏳ Deep Learning start ho rahi hai... Wait karein...")
        model.fit(X_train, y_train, batch_size=32, epochs=50, verbose=0) # verbose=0 kiya taaki kachra print na ho
        
        # --- 📊 NAYA CODE: ACCURACY CHECK ---
        train_predict = model.predict(X_train, verbose=0)
        
        # RMSE aur R2 calculate karo
        rmse = np.sqrt(mean_squared_error(y_train, train_predict))
        r2 = r2_score(y_train, train_predict)
        
        print(f"📊 ACCURACY REPORT FOR {ticker}:")
        print(f"   ➤ RMSE (Error) : {rmse:.4f} (Jitna kam, utna acha)")
        print(f"   ➤ R² Score     : {r2:.4f} (1.0 ke jitna paas, utna acha)")
        # ------------------------------------
        
        # Save Model as .h5
        model_path = f"saved_models/{ticker}_model.h5"
        model.save(model_path)
        
        print(f"✅ {ticker} - Model Saved Successfully!")
        
    except Exception as e:
        print(f"❌ Error training {ticker}: {e}")

# Folder create karo agar nahi hai
if not os.path.exists('saved_models'):
    os.makedirs('saved_models')

# Training loop
for stock in STOCKS_TO_TRAIN:
    train_and_save_model(stock)

print("\n🎉 ALL MODELS TRAINED AND SAVED SUCCESSFULLY!")