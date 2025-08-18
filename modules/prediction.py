import requests
import numpy as np
import pandas as pd
from prophet import Prophet

def get_market_chart(coin_id, days_to_predict, currency):
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-CiXq74m57raFnhxBi3jJttZU"
    }

    if days_to_predict == 1:
        freq = "5min"
        periods = int(24 * 60 / 5 * days_to_predict)
        api_days = 1
        add_hourly = True
    elif 2 <= days_to_predict <= 90:
        freq = "1h"
        periods = int(24 * days_to_predict)
        api_days = min(90, days_to_predict)
        add_hourly = True
    else:
        freq = "1D"
        periods = days_to_predict
        api_days = 365
        add_hourly = False

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": currency, "days": api_days}
    data = requests.get(url, headers=headers, params=params).json()

    if not data or "prices" not in data:
        raise ValueError("Error fetching market chart data.")

    prices = np.array(data["prices"])
    df = pd.DataFrame({
        "ds": pd.to_datetime(prices[:, 0], unit="ms"),
        "y": prices[:, 1]
    })

    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    if add_hourly:
        model.add_seasonality(name='hourly', period=1/24, fourier_order=5)
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    predictions = {str(ds): float(yhat) for ds, yhat in zip(forecast["ds"][-periods:], forecast["yhat"][-periods:])}
    return predictions
