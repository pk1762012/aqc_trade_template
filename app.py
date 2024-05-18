from datetime import timedelta
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    verify_jwt_in_request
)
from flask_jwt_extended.exceptions import JWTExtendedException, NoAuthorizationError
from functools import wraps
from angelone.angelone import AngelOne, Order

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=72)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_CSRF_IN_COOKIES'] = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'jwt_token'
app.config['JWT_SECRET_KEY'] = 'efae4076f8d0264edb6b9cad3c23f582a21280fa08fb4d53'
app.config['SECRET_KEY'] = 'db61afaa3d3a745724e414bb104032b6c229e2dba5e10517'
jwt = JWTManager(app)




def jwt_required_custom(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except NoAuthorizationError:
            return jsonify({'error': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def create_angel_one_instance(data):
    mandatory_fields = ['api_key']
    optional_fields = ['access_token', 'refresh_token', 'feed_token', 'userId', 'root', 'debug', 'timeout', 'proxies', 'pool', 'disable_ssl', 'privateKey']

    for field in mandatory_fields:
        if field not in data:
            raise ValueError(f"Mandatory field '{field}' is missing.")

    angel_one_params = {field: data[field] for field in mandatory_fields}
    for field in optional_fields:
        if field in data:
            angel_one_params[field] = data[field]

    return AngelOne(**angel_one_params)

@app.route('/api/generateSession', methods=['POST'])
#@jwt_required_custom
def generateSession():
   # user_email = get_jwt_identity()
    try:
        data = request.get_json()
        clientCode = data.get('clientCode')
        password = data.get('password')
        qr_value = data.get('qr_value')
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one_params = {'api_key': api_key}
        optional_fields = ['access_token', 'refresh_token', 'feed_token', 'userId', 'root', 'debug', 'timeout', 'proxies', 'pool', 'disable_ssl', 'privateKey']
        for field in optional_fields:
            if field in data:
                angel_one_params[field] = data.get(field)
        angel_one = AngelOne(**angel_one_params)
        response = angel_one.generateSession(clientCode, password, qr_value, api_key)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Unable to generate session, please contact your admin.'}), 403

@app.route('/api/terminateSession', methods=['POST', 'GET'])
#@jwt_required_custom
def terminateSession():
   # user_email = get_jwt_identity()
    try:
        data = request.get_json()
        clientCode = data.get('clientCode')
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.terminateSession(clientCode)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to terminate session, please contact your admin.'}), 403

@app.route('/api/generateToken', methods=['POST', 'GET'])
#@jwt_required_custom
def generateToken():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        refreshToken = data.get('refreshToken')
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.generateToken(refreshToken)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to generate token, please contact your admin.'}), 403

@app.route('/api/renewAccessToken', methods=['POST', 'GET'])
#@jwt_required_custom
def renewAccessToken():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.renewAccessToken()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to renew access token, please contact your admin.'}), 403

@app.route('/api/getProfile', methods=['POST', 'GET'])
#@jwt_required_custom
def getProfile():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        refreshToken = data.get('refreshToken')
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.getProfile(refreshToken)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to get profile, please contact your admin.'}), 403

@app.route('/api/placeOrder', methods=['POST', 'GET'])
#@jwt_required_custom
def placeOrder():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        order_data = data.get('order')
        if not order_data:
            raise ValueError("Mandatory field 'order' is missing.")
        order = Order(**order_data)
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.placeOrder(order)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to place order, please contact your admin.'}), 403

@app.route('/api/modifyOrder', methods=['POST', 'GET'])
#@jwt_required_custom
def modifyOrder():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        order_data = data.get('order')
        if not order_data:
            raise ValueError("Mandatory field 'order' is missing.")
        order = Order(**order_data)
        orderId = data.get('orderId')
        if not orderId:
            raise ValueError("Mandatory field 'orderId' is missing.")
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.modifyOrder(order, orderId)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to modify order, please contact your admin.'}), 403

@app.route('/api/cancelOrder', methods=['POST', 'GET'])
#@jwt_required_custom
def cancelOrder():
    #user_email = get_jwt_identity()
    try:
        data = request.get_json()
        variety = data.get('variety')
        if not variety:
            raise ValueError("Mandatory field 'variety' is missing.")
        orderId = data.get('orderId')
        if not orderId:
            raise ValueError("Mandatory field 'orderId' is missing.")
        api_key = data.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.cancelOrder(variety, orderId)
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to cancel order, please contact your admin.'}), 403

@app.route('/api/getOrderBook', methods=['POST', 'GET'])
#@jwt_required_custom
def getOrderBook():
   # user_email = get_jwt_identity()
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.getOrderBook()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to get order book, please contact your admin.'}), 403

@app.route('/api/getTradeBook', methods=['POST', 'GET'])
#@jwt_required_custom
def getTradeBook():
   # user_email = get_jwt_identity()
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.getTradeBook()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to get trade book, please contact your admin.'}), 403

@app.route('/api/getHolding', methods=['POST', 'GET'])
#@jwt_required_custom
def getHolding():
    #user_email = get_jwt_identity()
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.getHolding()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to get holding, please contact your admin.'}), 403

@app.route('/api/getPosition', methods=['POST', 'GET'])
#@jwt_required_custom
def getPosition():
    #user_email = get_jwt_identity()
    try:
        api_key = request.args.get('api_key')
        if not api_key:
            raise ValueError("Mandatory field 'api_key' is missing.")
        angel_one = AngelOne(api_key=api_key)
        response = angel_one.getPosition()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except:
        return jsonify({'success': False, 'message': 'Unable to get position, please contact your admin.'}), 403

if __name__ == '__main__':
    app.run(debug=True)
