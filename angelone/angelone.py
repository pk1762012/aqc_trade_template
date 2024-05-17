import ssl
from urllib.parse import urljoin

import requests as req
import socket
import re, uuid
import logzero
from logzero import logger
import logging
import json
import os
import time
# import totp

from angelone.angelOne_scrip_master import get_token_id_from_symbol
from body.Order import Order

log = logging.getLogger(__name__)

class AngelOne(object):
    _rootUrl = "https://apiconnect.angelbroking.com"
    _login_url = "https://smartapi.angelbroking.com/publisher-login"
    _default_timeout = 7 #seconds

    _routes = {
        "api.login": "/rest/auth/angelbroking/user/v1/loginByPassword",
        "api.logout": "/rest/secure/angelbroking/user/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

        "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
        "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
        "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
        "api.order.book":"/rest/secure/angelbroking/order/v1/getOrderBook",

        "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
        "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
        "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
    }

    #Fetching local and public IP addresses and MAC address of the device
    try:
        clientPublicIp = " " + req.get('https://api.ipify.org').text
        if " " in clientPublicIp:
            clientPublicIp = clientPublicIp.replace(" ", "")
        hostname = socket.gethostname()
        clientLocalIp = socket.gethostbyname(hostname)
    except Exception as e:
        print(e)
    finally:
        clientPublicIp = "106.193.147.98"
        clientLocalIp = "127.0.0.1"
    clientMacAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    accept = "application/json"
    userType = "USER"
    sourceID = "WEB"

    def __init__(self, api_key=None, access_token=None, refresh_token=None, feed_token=None, userId=None, root=None, debug=False, timeout=None, proxies=None, pool = None, disable_ssl=False, privateKey=None):
        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or self._rootUrl
        self.timeout = timeout or self._default_timeout
        self.Authorization = None
        self.clientLocalIP = self.clientLocalIp
        self.clientPublicIP = self.clientPublicIp
        self.clientMacAddress = self.clientMacAddress
        self.privateKey = api_key
        self.accept = self.accept
        self.userType = self.userType
        self.sourceID = self.sourceID

        #SSL Context creation
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.options |= ssl.OP_NO_TLSv1 #Disable TLS 1.0
        self.ssl_context.options |= ssl.OP_NO_TLSv1_1 #Disable TLS 1.1

        # Configure minimum TLS version to TLS 1.2
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if not disable_ssl:
            self.reqsession = req.Session()
            if pool is not None:
                reqadapter = req.adapters.HTTPAdapter(**pool)
                self.reqsession.mount("https://", reqadapter)
            else:
                reqadapter = req.adapters.HTTPAdapter()
                self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            #SSL disabled then use default ssl context
            self.reqsession = req

        # Create a log folder based on the current date
        log_folder = time.strftime("%Y-%m-%d", time.localtime())
        log_folder_path = os.path.join("angelOne_logs", log_folder)  # Construct the full path to the log folder
        os.makedirs(log_folder_path, exist_ok=True)  # Create the log folder if it doesn't exist
        log_path = os.path.join(log_folder_path, "app.log")  # Construct the full path to the log file
        logzero.logfile(log_path, loglevel=logging.ERROR)  # Output logs to a date-wise log file

        if pool:
            self.reqsession = req.Session()
            reqadapter = req.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            self.reqsession = req

        #disable requests ssl warning
        req.packages.urllib3.disable_warnings()

    def requestHeaders(self):
        return {
            "Content-type": self.accept,
            "X-ClientLocalIP": self.clientLocalIp,
            "X-ClientPublicIP": self.clientPublicIp,
            "X-MACAddress": self.clientMacAddress,
            "Accept": self.accept,
            "X-PrivateKey": self.privateKey,
            "X-UserType": self.userType,
            "X-SourceID": self.sourceID
        }

    def setSessionExpiryHook(self, method):
        if not callable(method):
            raise ValueError("Invalid imput type. Only functions are accepted")
        self.session_expiry_hook = method

    def login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s" % (self._login_url, self.api_key)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request"""
        params = parameters.copy() if parameters else {}

        uri = self._routes[route].format(**params)
        url = urljoin(self.root, uri)

        #Custom Headers
        headers = self.requestHeaders()

        if self.access_token:
            #set authorisation header
            auth_header = self.access_token
            headers["Authorization"] = "Bearer {}".format(auth_header)

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params, headers=headers))

        try:
            # print(json.dumps(params))
            # print(url)
            # print(headers)
            r = req.request(method,
                            url,
                            data=json.dumps(params) if method in ["POST", "PUT"] else None,
                            params=json.dumps(params) if method in ["GET","DELETE"] else None,
                            headers=headers,
                            verify=not self.disable_ssl,
                            allow_redirects=True,
                            timeout=self.timeout,
                            proxies=self.proxies)

        except Exception as e:
            logger.error(f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        #Validate content type
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))

            except ValueError:
                raise ("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            return data

        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))

    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)
    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)
    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)
    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def _getVariety(self, order):
        """Get order variety for angel one
            :returns 'STOPLOSS' or 'NORMAL'"""
        if order.isStopLossOrder:
            return "STOPLOSS"
        else:
            return "NORMAL"

    def _getTransactionType(self, order):
        """Get transaction type for angel one
            :returns 'BUY' or 'SELL'"""
        if order.transactionType == "BUY":
            return "BUY"
        else:
            return "SELL"

    def _getOrderType(self, order):
        """Get order type for angel one
            :returns 'LIMIT' or 'MARKET'"""
        if order.orderType == "MARKET":
            return "MARKET"
        else:
            return "LIMIT"

    def _getProductType(self, order):
        """Get product type for angel one
            :returns 'INTRADAY' or 'DELIVERY'"""
        if order.productType == "INTRADAY":
            return "INTRADAY"
        else:
            return "DELIVERY"

    def _getDuration(self, order):
        """Get duration for angel one
            :returns 'DAY' or 'IOC'"""
        if order.duration == "IOC":
            return "IOC"
        else:
            return "DAY"

    def _getExchange(self, order):
        """Get exchange for angel one
            :returns 'NSE' or 'BSE' or 'MCX - MCX Commodity' or 'NFO - NSE Future and Options' or 'CDS - Currency Derivative Segment' or 'BFO - BSE Future or Options' or None"""
        if order.exchange == "NSE":
            return "NSE"
        elif order.exchange == "BSE":
            return "BSE"
        elif order.exchange == "MCX":
            return "MCX"
        elif order.exchange == "NFO":
            return "NFO"
        elif order.exchange == "CDS":
            return "CDS"
        elif order.exchange == "BFO":
            return "BFO"
        else:
            return None

    def _getSymbolToken(self, order):
        """Get symbol token for angel one"""
        token = get_token_id_from_symbol(order.tradingSymbol, order.exchange)
        return str(token)

    def _getTradingSymbolFromOrder(self, order):
        if order.segment == "EQUITY":
            return order.tradingSymbol + "-EQ"
        else:
            return order.tradingSymbol

    def generateSession(self, clientCode, password, totp):

        params = {
            "clientcode": clientCode,
            "password": password, #actually the pin
            "totp": totp
        }
        loginResponse = self._postRequest("api.login", params)

        if loginResponse['status'] == True:
            jwtToken=loginResponse['data']['jwtToken']
            self.access_token = jwtToken
            refreshToken = loginResponse['data']['refreshToken']
            feedToken = loginResponse['data']['feedToken']
            self.refresh_token = refreshToken
            self.feed_token = feedToken
            user = self.getProfile(refreshToken)

            id = user['data']['clientcode']
            self.userId = id
            user['data']['jwtToken'] = "Bearer " + jwtToken
            user['data']['refreshToken'] = refreshToken
            user['data']['feedToken'] = feedToken

            return user
        else:
            return loginResponse

    def terminateSession(self, clientCode):
        logoutResponse = self._postRequest("api.logout", {"clientcode": clientCode})
        return logoutResponse

    def generateToken(self, refreshToken):
        response = self._postRequest('api.token', {
            "refreshToken": refreshToken
        })
        jwtToken = response['data']['jwtToken']
        feedToken = response['data']['feedToken']
        self.access_token = jwtToken
        self.feed_token = feedToken

        return response

    def renewAccessToken(self):
        response = self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token
        })

        tokenSet = {}

        if "jwtToken" in response:
            tokenSet['jwtToken'] = response['data']['jwtToken']

        tokenSet['clientcode'] = self.userId
        tokenSet['refreshToken'] = response['data']['refreshToken']

        return tokenSet

    def getProfile(self,refreshToken):
        user=self._getRequest("api.user.profile",{"refreshToken":refreshToken})
        return user

    def placeOrder(self, order: Order):
        params = {
            "variety": "NORMAL",
            "tradingsymbol": self._getTradingSymbolFromOrder(order),
            "symboltoken": self._getSymbolToken(order), #script to get token?
            "transactiontype": self._getTransactionType(order),
            "exchange": self._getExchange(order),
            "ordertype": self._getOrderType(order),
            "producttype": self._getProductType(order),
            "duration": self._getDuration(order),
            "price": str(order.price),
            "quantity": str(order.quantity),
            "stoploss": str(order.stopLossPrice),
            "squareoff": "0"
        }
        response = self._postRequest("api.order.place", params)
        # print(response)
        if response is not None and response.get('status', False):
            if 'data' in response and response['data'] is not None and 'orderid' in response['data']:
                orderResponse = response
                return orderResponse
            else:
                logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
        return None

    def modifyOrder(self, order: Order, orderId):
        params = {
            "variety": "NORMAL",
            "orderid": str(orderId),
            "ordertype": self._getOrderType(order),
            "producttype": self._getProductType(order),
            "duration": self._getDuration(order),
            "price": str(order.price),
            "quantity": str(order.quantity),
            "tradingsymbol": self._getTradingSymbolFromOrder(order),
            "symboltoken": self._getSymbolToken(order),
            "exchange": self._getExchange(order)
        }
        response = self._postRequest("api.order.modify", params)

        return response

    def cancelOrder(self, variety, orderId):
        params = {
            "variety": variety,
            "orderid": orderId
        }

        orderResponse = self._postRequest("api.order.cancel", params)
        return orderResponse

    def getOrderBook(self):
        response = self._getRequest("api.order.book")
        return response


    def getTradeBook(self):
        response = self._getRequest("api.trade.book")
        return response

    def getHolding(self):
        response = self._getRequest("api.holding")
        return response

    def getPosition(self):
        response = self._getRequest("api.position")
        return response