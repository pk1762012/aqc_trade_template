from flask import Flask, request, jsonify
from angelone.angelone import AngelOne, Order 
from buy_sell_angelone import TradingLogic
import pyotp

app = Flask(__name__)


tokens = {}

@app.route('/generatesession', methods=['POST'])
def login():
    try:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        client_code = request.json.get('clientCode')
        password = request.json.get('password')
        qrValue = request.json.get('qrValue')
        totp = pyotp.TOTP(qrValue).now()
        result = angel.generateSession(client_code, password, totp)
        if result['status']:
            tokens['access_token'] = result['data']['jwtToken']
            tokens['refresh_token'] = result['data']['refreshToken']
            tokens['feed_token'] = result['data']['feedToken']
            return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/terminatesession', methods=['POST'])
def logout():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            client_code = request.json.get('clientCode')
            result = angel.terminateSession(client_code)
            return jsonify(result)
        except Exception as error:
            print(error)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    

@app.route('/generatetoken', methods=['POST'])
def generate_token():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            refresh_token = request.json.get('refreshToken')
            result = angel.generateToken(refresh_token)
            return jsonify(result)
        except Exception as error:
            print(error)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/renewtoken', methods=['POST'])
def renew_token():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            result = angel.renewAccessToken()
            return jsonify(result)
        except Exception as error:
            print(error)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    
@app.route('/profile', methods=['GET'])
def get_profile():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
            apiKey = request.json.get('apiKey')
            angel = AngelOne(api_key=apiKey)
            refresh_token = request.json.get('refreshToken')
            result = angel.getProfile(refresh_token)
            return jsonify(result)
        except Exception as error:
            print(error)
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
    

@app.route('/funds', methods=['GET'])
def get_funds():
    jwt_token = tokens.get('access_token')
    #print(jwt_token)
    if jwt_token:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey, access_token=jwt_token)
        result = angel.getFunds()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

    

    
# buy_sell
@app.route('/process_trades', methods=['POST'])
def process_trades_route():
    data = request.json
    trading_logic = TradingLogic(apiKey=data.get('apiKey'), client_code=data.get('clientCode'), 
                                 password=data.get('password'), qrValue=data.get('qrValue'))
    results = trading_logic.process_trades(data['trades'])
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
