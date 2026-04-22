from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import yfinance as yf

app = Flask(__name__)
CORS(app)

def get_currency_symbol(ticker):
    ticker = ticker.upper()
    if ticker.endswith('.NS') or ticker.endswith('.BO'): return '₹'
    elif ticker.endswith('.L'): return '£'
    elif ticker.endswith('.DE') or ticker.endswith('.PA') or ticker.endswith('.AS'): return '€'
    elif ticker.endswith('.T'): return '¥'
    elif ticker.endswith('.TO'): return 'C$'
    elif ticker.endswith('.AX'): return 'A$'
    else: return '$'

@app.route('/predict_real_stock')
def predict_real_stock():
    ticker = request.args.get('ticker', 'AAPL')
    timeframe = request.args.get('timeframe', '1d') 
    currency = get_currency_symbol(ticker)
    
    if timeframe == '1m': period = "5d"
    elif timeframe == '1h': period = "730d"  
    else: period = "1000d" 

    try:
        data = yf.download(ticker, period=period, interval=timeframe)
        if data.empty:
            return jsonify({"error": f"No {timeframe} data found for {ticker}."}), 400
    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

    df = data[['Close']].copy()
    df['Prev_Close'] = df['Close'].shift(1)
    df.dropna(inplace=True)
    
    X = df[['Prev_Close']].values
    y = df['Close'].values
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    last_close = float(df['Close'].iloc[-1].item())
    next_pred = float(model.predict([[last_close]])[0].item())
    
    last_date = df.index[-1]
    
    if timeframe == '1m':
        next_date = last_date + pd.Timedelta(minutes=1)
        date_format = '%Y-%m-%d %H:%M'
    elif timeframe == '1h':
        next_date = last_date + pd.Timedelta(hours=1)
        date_format = '%Y-%m-%d %H:%M'
    else:
        next_date = last_date + pd.Timedelta(days=1)
        date_format = '%Y-%m-%d'

    dates = df.index[-100:].strftime(date_format).tolist()
    next_date_str = next_date.strftime(date_format)

    return jsonify({
        "ticker": ticker.upper(),
        "timeframe": timeframe,
        "currency_symbol": currency,
        "dates": dates,
        "next_date": next_date_str, 
        "actual": y_test[-100:].flatten().tolist(),
        "predicted": predictions[-100:].flatten().tolist(),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "last_price": round(last_close, 2),
        "prediction": round(next_pred, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)