import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from config import API_KEY

def get_market_chart(coin_id, predict_days=30, currency='usd'):
    history_days = 365

    response = requests.get(
        f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency={currency}&days={history_days}&api_key={API_KEY}'
    )
    ohlc_data = response.json()
    if not ohlc_data:
        return {"error": "No OHLC data available"}

    response = requests.get(
        f'https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&ids={coin_id}&api_key={API_KEY}'
    )
    market_list = response.json()
    if not market_list:
        return {"error": "No market data available"}
    market_data = market_list[0]
    current_price = market_data.get('current_price', 0)

    ohlc = np.array(ohlc_data)
    X = ohlc[:, [0, 4]]
    y = ohlc[:, 4]

    X = np.concatenate((
        X,
        np.full((len(X), 1), current_price)
    ), axis=1)

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)

    start_date = datetime.now()
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(predict_days)]

    last_price = y_pred[-1]
    predictions = {date: float(last_price) for date in dates}

    return predictions
