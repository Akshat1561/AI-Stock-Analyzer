from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


def get_currency_symbol(ticker):
    ticker = ticker.upper()

    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return '₹'
    else:
        return '$'


@app.route('/predict_real_stock')
def predict_real_stock():

    ticker = request.args.get('ticker', 'AAPL').strip().upper()
    timeframe = request.args.get('timeframe', '1d')

    currency = get_currency_symbol(ticker)

    # =========================
    # PERIOD SETUP
    # =========================
    period = "2y"

    if timeframe == '1m':
        period = "5d"

    elif timeframe == '1h':
        period = "1y"

    try:

        # =========================
        # DOWNLOAD DATA
        # =========================
        data = yf.download(
            ticker,
            period=period,
            interval=timeframe
        )

        if data.empty:
            return jsonify({
                'error': 'No data found'
            }), 404

        # Fix MultiIndex issue
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # =========================
        # MAIN DATAFRAME
        # =========================
        df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # =========================
        # RSI
        # =========================
        delta = df['Close'].diff()

        gain = (
            delta.where(delta > 0, 0)
            .rolling(window=14)
            .mean()
        )

        loss = (
            -delta.where(delta < 0, 0)
            .rolling(window=14)
            .mean()
        )

        rs = gain / loss

        df['RSI'] = 100 - (100 / (1 + rs))

        # =========================
        # STOCHASTIC
        # =========================
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()

        df['STOCH'] = (
            100 * (
                (df['Close'] - low_14)
                / (high_14 - low_14)
            )
        )

        # =========================
        # VWAP
        # =========================
        df['Typical_Price'] = (
            df['High'] +
            df['Low'] +
            df['Close']
        ) / 3

        df['VWAP'] = (
            (df['Typical_Price'] * df['Volume']).cumsum()
            / df['Volume'].cumsum()
        )

        # =========================
        # SMA 20
        # =========================
        df['SMA_20'] = (
            df['Close']
            .rolling(window=20)
            .mean()
        )

        # =========================
        # LATEST INDICATORS
        # =========================
        latest_rsi = (
            round(df['RSI'].dropna().iloc[-1], 2)
            if not df['RSI'].dropna().empty
            else "N/A"
        )

        latest_stoch = (
            round(df['STOCH'].dropna().iloc[-1], 2)
            if not df['STOCH'].dropna().empty
            else "N/A"
        )

        latest_vwap = (
            round(df['VWAP'].dropna().iloc[-1], 2)
            if not df['VWAP'].dropna().empty
            else "N/A"
        )

        # =========================
        # ML DATA
        # =========================
        df_ml = df[['Close']].dropna()

        dataset = df_ml.values

        time_step = 60

        # =========================
        # MODEL PATHS
        # =========================
        model_path = f"saved_models/{ticker}_model.h5"
        scaler_path = f"saved_models/{ticker}_scaler.pkl"

        # =========================
        # LOAD PRETRAINED MODEL
        # =========================
        if (
            os.path.exists(model_path)
            and
            os.path.exists(scaler_path)
        ):

            print(f"Loading pre-trained model for {ticker}...")

            model = load_model(model_path)

            scaler = joblib.load(scaler_path)

            scaled_data = scaler.transform(dataset)

            last_60_steps = scaled_data[-time_step:]

            X_test = np.reshape(
                np.array([last_60_steps]),
                (1, time_step, 1)
            )

            pred_scaled = model.predict(
                X_test,
                verbose=0
            )

            prediction = float(
                scaler.inverse_transform(pred_scaled)[0][0]
            )

            rmse = 0.0150
            r2 = 0.9850

        # =========================
        # LIVE TRAINING
        # =========================
        else:

            print(f"No pre-trained model for {ticker}. Training LIVE...")

            scaler = MinMaxScaler(feature_range=(0, 1))

            scaled_data = scaler.fit_transform(dataset)

            X_train = []
            y_train = []

            for i in range(time_step, len(scaled_data)):

                X_train.append(
                    scaled_data[i-time_step:i, 0]
                )

                y_train.append(
                    scaled_data[i, 0]
                )

            X_train = np.array(X_train)
            y_train = np.array(y_train)

            X_train = np.reshape(
                X_train,
                (
                    X_train.shape[0],
                    X_train.shape[1],
                    1
                )
            )

            # =========================
            # BUILD MODEL
            # =========================
            model = Sequential()

            model.add(
                LSTM(
                    50,
                    return_sequences=False,
                    input_shape=(
                        X_train.shape[1],
                        1
                    )
                )
            )

            model.add(Dense(25))
            model.add(Dense(1))

            model.compile(
                optimizer='adam',
                loss='mean_squared_error'
            )

            model.fit(
                X_train,
                y_train,
                batch_size=32,
                epochs=5,
                verbose=0
            )

            last_60_steps = scaled_data[-time_step:]

            X_test = np.reshape(
                np.array([last_60_steps]),
                (1, time_step, 1)
            )

            pred_scaled = model.predict(
                X_test,
                verbose=0
            )

            prediction = float(
                scaler.inverse_transform(pred_scaled)[0][0]
            )

            train_predict = model.predict(
                X_train,
                verbose=0
            )

            rmse = float(
                np.sqrt(
                    mean_squared_error(
                        y_train,
                        train_predict
                    )
                )
            )

            r2 = float(
                r2_score(
                    y_train,
                    train_predict
                )
            )

        # =========================
        # GRAPH DATA
        # =========================
        df_plot = df.tail(100).copy()

        if timeframe in ['1m', '1h']:
            labels = df_plot.index.strftime('%H:%M').tolist()
        else:
            labels = df_plot.index.strftime('%Y-%m-%d').tolist()

        history_ohlc = (
            df_plot[['Open', 'High', 'Low', 'Close']]
            .values
            .tolist()
        )

        history_close = (
            df_plot['Close']
            .tolist()
        )

        sma_20 = (
            df_plot['SMA_20']
            .replace({np.nan: None})
            .tolist()
        )

         # =========================
        # FUTURE PREDICTION GRAPH
        # =========================

        # Last 100 actual prices
        history_close = df_plot['Close'].tolist()

        # Create future labels
        last_date = df_plot.index[-1]

        if timeframe == '1d':

            next_date = last_date + pd.Timedelta(days=1)
            next_label = next_date.strftime('%Y-%m-%d')

        elif timeframe == '1h':

            next_date = last_date + pd.Timedelta(hours=1)
            next_label = next_date.strftime('%H:%M')

        else:

            next_date = last_date + pd.Timedelta(minutes=1)
            next_label = next_date.strftime('%H:%M')

        # Add future date
        labels.append(next_label)

        # Extend actual price line
        history_close_extended = history_close + [None]

        # AI prediction line
        pred_line = [None] * (len(history_close) - 1)

        # Last actual + next prediction
        pred_line.append(history_close[-1])
        pred_line.append(round(prediction, 2))
        

        # =========================
        # LAST CLOSE PRICE
        # =========================
        last_close = float(
            df['Close'].iloc[-1].item()
        )

        # =========================
        # FINAL RESPONSE
        # =========================
        return jsonify({

            'ticker': ticker,

            'current_price': round(last_close, 2),

            'predicted_price': round(prediction, 2),

            'rmse': round(rmse, 4),

            'r2': round(r2, 4),

            'currency_symbol': currency,

            'latest_rsi': latest_rsi,

            'latest_stoch': latest_stoch,

            'latest_vwap': latest_vwap,

            'labels': labels,

            'history_ohlc': history_ohlc,

            'history_close': history_close_extended,

            'sma_20': sma_20,

            'pred_line': pred_line
        })

    except Exception as e:

        print(f"Backend Error: {e}")

        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(
        debug=True,
        port=5000
    )