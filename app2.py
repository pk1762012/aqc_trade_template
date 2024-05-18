from flask import Flask, request, jsonify
from angelone.angelone import AngelOne, Order 
import pyotp
from flask import Flask, request, jsonify
from buy_sell_angelone import DatabaseClient, TradingLogic


app = Flask(__name__)

db_client = DatabaseClient("mongodb://localhost:27017/")
trading_logic = TradingLogic(db_client, available_balance=50000)  

angel = AngelOne(api_key="dWjWcggF") # hardcoded api
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
    try:
        client_code = request.json.get('clientCode')
        password = request.json.get('password')
        qrValue = request.json.get('qrValue')
        totp = pyotp.TOTP(qrValue).now()
        result = angel.generateSession(client_code, password, totp)
        if result['status']:
            save_tokens(result['data']['jwtToken'], result['data']['refreshToken'], result['data']['feedToken'])
        return jsonify(result)
    except Exception as e:
        print(e)

@app.route('/terminatesession', methods=['POST'])
def logout():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        try:
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
        result = angel.getOrderBook()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/trade/book', methods=['GET'])
def get_trade_book():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        result = angel.getTradeBook()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/holdings', methods=['GET'])
def get_holdings():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        result = angel.getHolding()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401

@app.route('/positions', methods=['GET'])
def get_positions():
    jwt_token = request.headers.get('Authorization')
    if jwt_token:
        result = angel.getPosition()
        return jsonify(result)
    else:
        return jsonify({"error": "Authorization token is missing"}), 401
    
# buy_sell
@app.route('/process_trades', methods=['POST'])
def process_trades_route():
    try:
        data = request.get_json()  
        customer_confirms = data.get('customer_confirms', False)

        if customer_confirms:
            trading_logic.process_trades(customer_confirms=True)
            return jsonify({"status": "success", "message": "Trades processed successfully."}), 200
        else:
            return jsonify({"status": "failure", "message": "Trade canceled by customer."}), 400
    except Exception as error:
        print(error)


if __name__ == '__main__':
    app.run(debug=True)
