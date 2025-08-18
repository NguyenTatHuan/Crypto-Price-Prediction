from flask import Flask, request, jsonify
from modules.prediction import get_market_chart
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    coin_id = data.get('coin_id')
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-CiXq74m57raFnhxBi3jJttZU"
    }
    coin_name = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}', headers=headers).json().get('name', coin_id)
    days = data.get('days', 30)
    currency = data.get('currency', 'usd')
    predictions = get_market_chart(coin_id, days, currency)
    return jsonify({'coin_id': coin_id, 'coin_name': coin_name, 'currency': currency, 'predictions': predictions})

if __name__ == '__main__':
    app.run()