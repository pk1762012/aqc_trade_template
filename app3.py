from flask import Flask, request, jsonify
from angelone.angelone import AngelOne, Order 
import pyotp

app = Flask(__name__)

##################### api with each request ###################

tokens = {
    "jwtToken": None,
    "refreshToken": None,
    "feedToken": None
}

def save_tokens(jwt_token, refresh_token, feed_token):
    """
    Save the tokens in the global dictionary.
    """
    tokens["jwtToken"] = jwt_token
    tokens["refreshToken"] = refresh_token
    tokens["feedToken"] = feed_token

@app.route('/generatesession', methods=['POST'])
def login():
    client_code = request.json.get('clientCode')
    password = request.json.get('password')
    qrValue = request.json.get('qrValue')
    totp = pyotp.TOTP(qrValue).now()
    apiKey = request.json.get('apiKey')
    angel = AngelOne(api_key=apiKey)
    result = angel.generateSession(client_code, password, totp)
    if result['status']:
        save_tokens(result['data']['jwtToken'], result['data']['refreshToken'], result['data']['feedToken'])
    return jsonify(result)

@app.route('/terminatesession', methods=['POST'])
def logout():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        client_code = request.json.get('clientCode')
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.terminateSession(client_code)
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/generatetoken', methods=['POST'])
def generate_token():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        refresh_token = request.json.get('refreshToken')
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.generateToken(refresh_token)
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    

@app.route('/renewtoken', methods=['POST'])
def renew_token():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.renewAccessToken()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/profile', methods=['GET'])
def get_profile():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        refresh_token = request.json.get('refreshToken')
        result = angel.getProfile(refresh_token)
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/order/place', methods=['POST'])
def place_order():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            order_details = request.json
            order = Order(**order_details)
            result = angel.placeOrder(order)
            return jsonify(result)
        except Exception as error:
            print(error)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

'''@app.route('/order/place', methods=['POST'])
def place_orders():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            orders_details = request.json.get('orders')  
            results = []
            for order_detail in orders_details:
                order = Order(**order_detail)
                result = angel.placeOrder(order)
                results.append(result)
            return jsonify(results)
        except Exception as e:
            print(e)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401'''


@app.route('/order/modify', methods=['POST'])
def modify_order():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        order_details = request.json.get('order')
        order_id = request.json.get('orderId')
        order = Order(**order_details)
        result = angel.modifyOrder(order, order_id)
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/order/cancel', methods=['POST'])
def cancel_order():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        variety = request.json.get('variety')
        order_id = request.json.get('orderId')
        result = angel.cancelOrder(variety, order_id)
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/order/book', methods=['GET'])
def get_order_book():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.getOrderBook()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/trade/book', methods=['GET'])
def get_trade_book():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.getTradeBook()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/holdings', methods=['GET'])
def get_holdings():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.getHolding()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/positions', methods=['GET'])
def get_positions():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        result = angel.getPosition()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

if __name__ == '__main__':
    app.run(debug=True)
