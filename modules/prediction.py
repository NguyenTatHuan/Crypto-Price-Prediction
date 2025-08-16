import requests
import numpy as np
from sklearn.linear_model import LinearRegression
import time
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

def get_market_chart(coin_id, days, currency):
    end_timestamp = int(time.time())
    start_timestamp = end_timestamp - int(days) * 24 * 60 * 60

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-CiXq74m57raFnhxBi3jJttZU"
    }

    ohlc_data = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency={currency}&days={days}', headers=headers).json()
    ohlc = np.array(ohlc_data)

    date = time.strftime('%d-%m-%Y', time.gmtime(start_timestamp))
    history_data = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date}', headers=headers).json()
    
    market_data = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&ids={coin_id}', headers=headers).json()[0]

    X = ohlc[:, 0:5]
    y = ohlc[:, 4]
    X = np.concatenate((X, np.full((len(X), 1), history_data['market_data']['current_price'][currency]), np.full((len(X), 1), market_data['current_price'])), axis=1)

    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    if days == 1:
        step_hours = 0.5
    elif days in [7, 14, 30]:
        step_hours = 4
    elif days in [90, 180, 365]:
        step_hours = 96
    else:
        step_hours = 24

    start_date = datetime.now()
    if step_hours == 0.5:
        if start_date.minute < 30:
            start_date = start_date.replace(minute=0, second=0, microsecond=0)
        else:
            start_date = start_date.replace(minute=30, second=0, microsecond=0)
    else:
        if start_date.minute > 0 or start_date.second > 0:
            start_date = start_date.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            start_date = start_date.replace(minute=0, second=0, microsecond=0)

    dates = [
        (start_date + timedelta(hours=i * step_hours)).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(len(y_pred))
    ]

    predictions = {date: pred for date, pred in zip(dates, y_pred)}
    return predictions