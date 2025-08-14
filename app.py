from flask import Flask, request, jsonify
from modules.prediction import get_market_chart

app = Flask(__name__)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        data = request.json
        coin_id = data.get('coin_id')
        predict_days = int(data.get('predict_days', 30))
        currency = data.get('currency', 'usd')

        predictions = get_market_chart(coin_id, predict_days, currency)
        return jsonify({'coin_id': coin_id, 'currency': currency, 'predictions': predictions})
    else:
        return "OK", 200

if __name__ == '__main__':
    app.run()
