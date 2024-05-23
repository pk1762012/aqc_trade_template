from flask import Flask, request, jsonify
from angelone.angelone import AngelOne, Order 
from buy_sell_angelone import TradingLogic
from flask_cors import CORS
import pyotp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/generate-session', methods=['POST'])
def login():
    try:
        apiKey = request.json.get('apiKey')
        angel = AngelOne(api_key=apiKey)
        client_code = request.json.get('clientCode')
        password = request.json.get('password')
        qrValue = request.json.get('qrValue')
        totp = pyotp.TOTP(qrValue).now()
        result = angel.generateSession(client_code, password, totp)
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@app.route('/terminate-session', methods=['POST'])
def logout():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            client_code = data.get('clientCode')
            result = angel.terminateSession(client_code)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    

@app.route('/generate-token', methods=['POST'])
def generate_token():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            refresh_token = data.get('refreshToken')
            result = angel.generateToken(refresh_token)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/renew-token', methods=['POST'])
def renew_token():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.renewAccessToken()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    
@app.route('/profile', methods=['GET'])
def get_profile():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            refresh_token = request.json.get('refreshToken')
            result = angel.getProfile(refresh_token)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/place-order', methods=['POST'])
def place_order():
    data = request.json
    auth_data = data.get('auth', {})
    jwt_token = auth_data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = auth_data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            order_data = data.get('order', {})
            
            order = Order(**order_data)
            result = angel.placeOrder(order)
            if result is None or not result.get('status', True): 
                error_message = result.get('message', 'Unknown error')
                error_code = result.get('errorcode', 'Unknown error code')
                return jsonify({"error": error_message, "errorcode": error_code}), 400
            return jsonify(result)  
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/modify-order', methods=['POST'])
def modify_order():
    data = request.json
    auth_data = data.get('auth', {})
    jwt_token = auth_data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = auth_data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            order_data = data.get('order', {})
            order_id = order_data.pop('orderId', None)  

            if not order_id:
                return jsonify({"error": "Order ID is missing"}), 400

            order = Order(**order_data)
            result = angel.modifyOrder(order, order_id)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    data = request.json
    auth_data = data.get('auth', {})
    jwt_token = auth_data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = auth_data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            order_data = data.get('order', {})
            variety = order_data.get('variety')
            order_id = order_data.get('orderId')

            if not order_id:
                return jsonify({"error": "Order ID is missing"}), 400

            result = angel.cancelOrder(variety, order_id)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/order-book', methods=['GET'])
def get_order_book():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.getOrderBook()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    
@app.route('/single-order-status', methods=['GET'])
def get_order_status():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            uniqueorderid = data.get('uniqueorderid')
            if not uniqueorderid:
                return jsonify({"error": "Order ID is missing"}), 400
            result = angel.getOrderStatus(uniqueorderid)
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401


@app.route('/trade-book', methods=['GET'])
def get_trade_book():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.getTradeBook()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/holdings', methods=['GET'])
def get_holdings():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.getHolding()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/positions', methods=['GET'])
def get_positions():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.getPosition()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    

@app.route('/funds', methods=['GET'])
def get_funds():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            angel = AngelOne(api_key=apiKey, access_token=jwt_token)
            result = angel.getFunds()
            return jsonify(result)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

    
# buy_sell
@app.route('/process-trades', methods=['POST'])
def process_trades_route():
    data = request.json
    jwt_token = data.get('jwtToken')
    if jwt_token:
        try:
            apiKey = data.get('apiKey')
            trading_logic = TradingLogic(api_key=apiKey, access_token=jwt_token )
            results = trading_logic.process_trades(data['trades'])
            return jsonify(results)
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/', methods=['GET'])
def server_running():
    return 'Server Active and running'

if __name__ == '__main__':
    app.run(debug=True)
