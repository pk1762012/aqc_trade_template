from iifl_new.controllers import *
from flask import Flask, request, jsonify
from flask_cors import CORS
import pyotp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/login-mobile-vendor', methods=['POST'])
def login_mobile_vendor():
    data = request.json
    try:
        response = LoginRequestMobileForVendor()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login-v2', methods=['POST'])
def login_v2():
    data = request.json
    client_code = data.get('clientCode')
    password = data.get('password')
    my2pin = data.get('my2pin')
    try:
        response = LoginRequestV2(client_code, password, my2pin)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order-request', methods=['POST'])
def order_request():
    data = request.json
    order = Order(**data) 
    try:
        response = OrderRequest(order)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/modify-order', methods=['POST'])
def modify_order():
    data = request.json
    order = Order(**data['order']) 
    traded_qty = data.get('tradedQty')
    exch_order_id = data.get('exchOrderId')
    try:
        response = ModifyOrderRequest(order, traded_qty, exch_order_id)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    data = request.json
    order = Order(**data['order'])
    traded_qty = data.get('tradedQty')
    exch_order_id = data.get('exchOrderId')
    try:
        response = CancelOrderRequest(order, traded_qty, exch_order_id)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/holding-v2', methods=['POST'])
def holding_v2():
    client_code = request.json.get('clientCode')
    try:
        response = HoldingV2(client_code)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/margin-v3', methods=['POST'])
def margin_v3():
    client_code = request.json.get('clientCode')
    try:
        response = MarginV3(client_code)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/order-book-v2', methods=['POST'])
def order_book_v2():
    client_code = request.json.get('clientCode')
    try:
        response = OrderBookV2(client_code)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/trade-book-v1', methods=['POST'])
def trade_book_v1():
    client_code = request.json.get('clientCode')
    try:
        response = TradeBookV1(client_code)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/trade-information', methods=['POST'])
def trade_information():
    data = request.json
    client_code = data.get('clientCode')
    trade_info_list = data.get('tradeInformationList')
    try:
        response = TradeInformation(client_code, trade_info_list)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


