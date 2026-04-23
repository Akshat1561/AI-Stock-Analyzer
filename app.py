from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import yfinance as yf
import os

app = Flask(__name__)
CORS(app)

# --- 🌐 ROUTES FOR HTML PAGES ---

@app.route('/')
def home():
    # Ye index.html ko serve karega (templates folder se)
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Ye dashboard.html ko serve karega
    return render_template('dashboard.html')

# --- 📊 API ENDPOINT FOR STOCK DATA ---

def get_currency_symbol(ticker):
    ticker = ticker.upper()
    if ticker.endswith('.NS') or ticker.endswith('.BO'): return '₹'
    else: return '$'

@app.route('/predict_real_stock')
def predict_real_stock():
    ticker = request.args.get('ticker', 'AAPL')
    timeframe = request.args.get('timeframe', '1d')
    currency = get_currency_symbol(ticker)
    
    period = "1000d"
    if timeframe == '1m': period = "5d"
    elif timeframe == '1h': period = "730d"

    try:
        data = yf.download(ticker, period=period, interval=timeframe)
        if data.empty:
            return jsonify({'error': 'No data found'}), 404
        
        df = data[['Close']].copy()
        df['S_1'] = df['Close'].shift(1)
        df = df.dropna()

        X = df[['S_1']].values
        y = df['Close'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_close = float(df['Close'].iloc[-1].item())
        prediction = float(model.predict([[last_close]])[0].item())
        
        # Chart ke liye pichle 100 points
        history = df['Close'].tail(100).tolist()
        labels = [str(i) for i in range(len(history))]

        return jsonify({
            'ticker': ticker,
            'current_price': round(last_close, 2),
            'predicted_price': round(prediction, 2),
            'currency_symbol': currency,
            'history': history,
            'labels': labels
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # App ko local pe host karne ke liye
    app.run(debug=True, port=5000)