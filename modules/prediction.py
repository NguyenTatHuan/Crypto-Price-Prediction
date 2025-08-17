import requests
import numpy as np
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
import math

def get_market_chart(coin_id, days, currency):
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-CiXq74m57raFnhxBi3jJttZU"
    }

    if days == 1:
        ohlc_days, freq, periods = 1, '30min', 48
    elif days <= 30:
        ohlc_days, freq, periods = 30, '4h', days * 6
    else:
        ohlc_days, freq, periods = 365, '4D', math.ceil(days / 4)

    ohlc_data = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency={currency}&days={ohlc_days}', headers=headers).json()
    if not ohlc_data or isinstance(ohlc_data, dict):
        raise ValueError("Error fetching OHLC data.")
    ohlc = np.array(ohlc_data)

    df = pd.DataFrame({
        "ds": pd.to_datetime(ohlc[:, 0], unit="ms"),
        "y": ohlc[:, 4]
    })

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    predictions = {}
    if days <= 30:
        start_index = -periods
        for ds, yhat in zip(forecast['ds'][start_index:], forecast['yhat'][start_index:]):
            predictions[str(ds)] = float(yhat)
    else:
        start_date = datetime.now().date() + timedelta(days=1)
        for i, yhat in enumerate(forecast['yhat'][-periods:]):
            pred_date = start_date + timedelta(days=i*4)
            predictions[str(pred_date)] = float(yhat)

    return predictions