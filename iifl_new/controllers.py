import sys, os
import json
import urllib3

from body.Order import Order
from .common_utils import common_util
import requests as req
import http.cookiejar

cookielib = http.cookiejar

http = urllib3.PoolManager()
env = common_util.get_env()

cookie_=common_util.get_cookie()
jwt_=common_util.get_jwt()

AppSource = env.get('credentials', 'AppSource')

def LoginRequestMobileForVendor():
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        Email_id = env.get('credentials', 'Email_id')
        ContactNumber = env.get('credentials', 'ContactNumber')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        url = env.get('urls', 'loginRequestMobileForVendor')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        payload = {
            "head": {
                "requestCode": "IIFLMarRQLoginForVendor",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": common_util.auth.encrypt(UserId),
                "password": common_util.auth.encrypt(Password)
            },
            "body": {
                "Email_id": Email_id,
                "ContactNumber": ContactNumber,
                "LocalIP": "192.168.88.41",
                "PublicIP": "192.168.88.42"
            }
        }

        print(json.dumps(payload))
        print(header)
        session = req.Session()
        resp = session.post(url=url, headers=header, data=json.dumps(payload))
        print(resp.cookies)

        resp = json.loads(resp.text)

        common_util.write_cookie(session.cookies.get_dict().get('IIFLMarcookie'))
        resp['cookies'] = session.cookies.get_dict()
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def LoginRequestV2(clientCode, password, my2pin):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        ClientCode = clientCode
        Password_ = password
        HDSerialNumber = ''
        MACAddress = ''
        MachineID = ''
        VersionNo = ''
        My2PIN = my2pin

        url = env.get('urls', 'LoginRequestV2')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        payload = {
            "head": {
                "requestCode": "IIFLMarRQLoginRequestV4",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": common_util.auth.encrypt(ClientCode),
                "Password": common_util.auth.encrypt(Password_),
                "HDSerialNumber": HDSerialNumber,
                "MACAddress": MACAddress,
                "MachineID": MachineID,
                "VersionNo": VersionNo,
                "RequestNo": 1,
                "My2PIN": common_util.auth.encrypt(My2PIN),
                "ConnectionType": 1,
                "LocalIP": "192.168.88.41",
                "PublicIP": "192.168.88.42"
            }
        }

        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        common_util.write_jwt(resp['body']['Token'])
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def OrderRequest(order: Order):
    """Place a order on the IIFL platform"""
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        AppSource = env.get('credentials', 'AppSource')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "_ReqData": {
                "head": {
                    "requestCode": "IIFLMarRQOrdReq",
                    "key": UserKey,
                    "appVer": "1.0",
                    "appName": AppName,
                    "osName": "Android",
                    "userId": UserId,
                    "password": Password
                },
                "body": {
                    "ClientCode": order.clientCode,
                    "OrderRequesterCode": order.clientCode,
                    "OrderFor": "P",
                    "Exchange": order.exchange,
                    "ExchangeType": order.segment,
                    "Price": order.price,

                    "OrderID": 3,  # random value

                    "OrderType": order.transactionType,
                    "Qty": order.quantity,
                    "OrderDateTime": '/Date(' + str(common_util.time_milli_second()) + ')/',

                    "TradedQty": 0,
                    # For placing fresh order, value should be 0. For modification/cancellation, send the actual traded qty.

                    "ScripCode": order.scripCode,  # stock code

                    "AtMarket": order.isAtMarket,  # false --> limit order true --> market order
                    "RemoteOrderID": "s000220360",  ##unique id for each order

                    "ExchOrderID": "0",
                    # Send 0 for fresh order and for modify cancel send the exchange order id received from exchange.
                    "DisQty": order.discQuantity,  # display qty

                    "StopLossPrice": order.stopLossPrice,
                    # shoould be checked outside before implementing here
                    "IsStopLossOrder": order.isStopLossOrder,

                    "IOCOrder": order.isIOCOrder,
                    "IsIntraday": order.isIntraday,

                    "ValidTillDate": '/Date(' + str(common_util.time_milli_second(expiry_time=True)) + ')/',
                    "PublicIP": "192.168.84.215",
                    "iOrderValidity": order.iOrderValidity,
                    "IsVTD": order.isVTD,
                    "AHPlaced": order.isAHPlaced
                }
            },
            "AppSource": int(AppSource)
        }
        url = env.get('urls', 'OrderRequest')

        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }

        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def ModifyOrderRequest(order: Order, tradedQnty, exchOrderID):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        AppSource = env.get('credentials', 'AppSource')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "_ReqData": {
                "head": {
                    "requestCode": "IIFLMarRQOrdReq",
                    "key": UserKey,
                    "appVer": "1.0",
                    "appName": AppName,
                    "osName": "Android",
                    "userId": UserId,
                    "password": Password
                },
                "body": {
                    "ClientCode": order.clientCode,
                    "OrderRequesterCode": order.clientCode,
                    "OrderFor": "M",
                    "Exchange": order.exchange,
                    "ExchangeType": order.segment,
                    "Price": order.price,

                    "OrderID": 3,  # random value

                    "OrderType": order.transactionType,
                    "Qty": order.quantity,
                    "OrderDateTime": '/Date(' + str(common_util.time_milli_second()) + ')/',

                    "TradedQty": tradedQnty,
                    # For placing fresh order, value should be 0. For modification/cancellation, send the actual traded qty.

                    "ScripCode": order.scripCode,  # stock code

                    "AtMarket": order.isAtMarket,  # false --> limit order true --> market order
                    "RemoteOrderID": "s000220360",  ##unique id for each order

                    "ExchOrderID": exchOrderID,
                    # Send 0 for fresh order and for modify cancel send the exchange order id received from exchange.
                    "DisQty": order.discQuantity,  # display qty

                    "StopLossPrice": order.stopLossPrice,
                    # shoould be checked outside before implementing here
                    "IsStopLossOrder": order.isStopLossOrder,

                    "IOCOrder": order.isIOCOrder,
                    "IsIntraday": order.isIntraday,

                    "ValidTillDate": '/Date(' + str(common_util.time_milli_second(expiry_time=True)) + ')/',
                    "PublicIP": "192.168.84.215",
                    "iOrderValidity": order.iOrderValidity,
                    "IsVTD": order.isVTD,
                    "AHPlaced": order.isAHPlaced
                }
            },
            "AppSource": int(AppSource)
        }
        url = env.get('urls', 'OrderRequest')

        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }

        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def CancelOrderRequest(order: Order, tradedQnty, exchOrderID):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        AppSource = env.get('credentials', 'AppSource')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "_ReqData": {
                "head": {
                    "requestCode": "IIFLMarRQOrdReq",
                    "key": UserKey,
                    "appVer": "1.0",
                    "appName": AppName,
                    "osName": "Android",
                    "userId": UserId,
                    "password": Password
                },
                "body": {
                    "ClientCode": order.clientCode,
                    "OrderRequesterCode": order.clientCode,
                    "OrderFor": "C",
                    "Exchange": order.exchange,
                    "ExchangeType": order.segment,
                    "Price": order.price,

                    "OrderID": 3,  # random value

                    "OrderType": order.transactionType,
                    "Qty": order.quantity,
                    "OrderDateTime": '/Date(' + str(common_util.time_milli_second()) + ')/',

                    "TradedQty": tradedQnty,
                    # For placing fresh order, value should be 0. For modification/cancellation, send the actual traded qty.

                    "ScripCode": order.scripCode,  # stock code

                    "AtMarket": order.isAtMarket,  # false --> limit order true --> market order
                    "RemoteOrderID": "s000220360",  ##unique id for each order

                    "ExchOrderID": exchOrderID,
                    # Send 0 for fresh order and for modify cancel send the exchange order id received from exchange.
                    "DisQty": order.discQuantity,  # display qty

                    "StopLossPrice": order.stopLossPrice,
                    # shoould be checked outside before implementing here
                    "IsStopLossOrder": order.isStopLossOrder,

                    "IOCOrder": order.isIOCOrder,
                    "IsIntraday": order.isIntraday,

                    "ValidTillDate": '/Date(' + str(common_util.time_milli_second(expiry_time=True)) + ')/',
                    "PublicIP": "192.168.84.215",
                    "iOrderValidity": order.iOrderValidity,
                    "IsVTD": order.isVTD,
                    "AHPlaced": order.isAHPlaced
                }
            },
            "AppSource": int(AppSource)
        }
        url = env.get('urls', 'OrderRequest')

        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }

        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def HoldingV2(clientCode):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "head": {
                "requestCode": "IIFLMarRQHoldingV2",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": clientCode
            }
        }

        url = env.get('urls', 'HoldingV2')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def MarginV3(clientCode):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "head": {
                "requestCode": "IIFLMarRQMarginV3",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": clientCode
            }
        }

        url = env.get('urls', 'MarginV3')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def OrderBookV2(clientCode):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "head": {
                "requestCode": "IIFLMarRQOrdBkV2",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": clientCode
            }
        }

        url = env.get('urls', 'OrderBookV2')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        print(payload)
        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def TradeBookV1(clientCode):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "head": {
                "requestCode": "IIFLMarRQTrdBkV1",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": clientCode
            }
        }

        url = env.get('urls', 'TradeBookV1')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e

def TradeInformation(clientCode,tradeInformationList):
    try:
        UserKey = env.get('credentials', 'UserKey')
        AppName = env.get('credentials', 'AppName')
        UserId = env.get('credentials', 'UserId')
        Password = env.get('credentials', 'Password')
        EncryKey = env.get('credentials', 'EncryKey')
        OAS_key = env.get('credentials', 'Ocp-Apim-Subscription-Key')

        payload = {
            "head": {
                "requestCode": "IIFLMarRQTrdInfo",
                "key": UserKey,
                "appVer": "1.0",
                "appName": AppName,
                "osName": "Android",
                "userId": UserId,
                "password": Password
            },
            "body": {
                "ClientCode": clientCode,
                "TradeInformationList": tradeInformationList
            }
        }

        url = env.get('urls', 'TradeInformation')
        header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": OAS_key
        }
        cookies = req.cookies.RequestsCookieJar()
        cookies.set('IIFLMarcookie', cookie_, domain='dataservice.iifl.in')
        resp = req.post(url=url, headers=header, data=json.dumps(payload), cookies=cookies)

        resp = json.loads(resp.text)
        print(resp)
        return resp

    except Exception as e:
        print(e)
        return e