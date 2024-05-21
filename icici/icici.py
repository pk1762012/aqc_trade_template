import hashlib
from urllib.parse import urljoin
import requests as req
import logzero
from logzero import logger
import logging
import json
import os
import time
from datetime import datetime


from body.Order import Order

log = logging.getLogger(__name__)

class ICICI(object):
    _rootUrl = "https://api.icicidirect.com"
    _login_url = "https://api.icicidirect.com/apiuser/login"
    _default_timeout = 7 #seconds

    _routes = {
        "api.customer.details": "/breezeapi/api/v1/customerdetails",
        "api.holding": "/breezeapi/api/v1/dematholdings",

        "api.order.place": "/breezeapi/api/v1/order",
    }

    def __init__(self, app_key=None, session_token=None, debug=False, timeout=None, secret_key=None):
        self.app_key = app_key
        self.session_token = session_token
        self.debug = debug
        self.timeout = timeout or self._default_timeout
        self.secret_key = secret_key

        # Create a log folder based on the current date
        log_folder = time.strftime("%Y-%m-%d", time.localtime())
        log_folder_path = os.path.join("angelOne_logs", log_folder)  # Construct the full path to the log folder
        os.makedirs(log_folder_path, exist_ok=True)  # Create the log folder if it doesn't exist
        log_path = os.path.join(log_folder_path, "app.log")  # Construct the full path to the log file
        logzero.logfile(log_path, loglevel=logging.ERROR)  # Output logs to a date-wise log file

    def _getTimestamp(self):
        return (datetime.utcnow().isoformat()[:19] + '.000Z')

    def _getChecksum(self, time_stamp, payload, secret_key):
        checksum = hashlib.sha256((time_stamp + payload + secret_key).encode("utf-8")).hexdigest()
        return checksum

    def requestHeaders(self, payload=None):
        """Populate the Checksum from the request call since it requires payload"""
        if(payload is None):
            return {
                'Content-Type': 'application/json'
            }

        return {
            'Content-Type': 'application/json',
            'X-Checksum': 'token '+ self._getChecksum(self._getTimestamp(), payload, self.secret_key),
            'X-Timestamp': self._getTimestamp(),
            'X-AppKey': self.app_key,
            'X-SessionToken': self.session_token
        }

    def login_url(self):
        return "%s?api_key=%s" % (self._login_url, self.app_key)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request"""
        params = parameters.copy() if parameters else {}

        uri = self._routes[route].format(**params)
        url = urljoin(self.root, uri)

        # Custom Headers
        if (route == "api.customer.details"):
            headers = self.requestHeaders()
        else:
            headers = self.requestHeaders(json.dumps(params))

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params,
                                                                          headers=headers))

        try:
            # print(json.dumps(params))
            # print(url)
            # print(headers)
            r = req.request(method,
                            url,
                            data=json.dumps(params) if method in ["POST", "PUT"] else None,
                            params=json.dumps(params) if method in ["GET","DELETE"] else None,
                            headers=headers,
                            # verify=not self.disable_ssl,
                            allow_redirects=True,
                            timeout=self.timeout
                            # proxies=self.proxies
                            )
        except Exception as e:
            logger.error(f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))

            except ValueError:
                raise ("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            return data
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


    def getCustomerDetails(self):
        params = {
            "SessionToken": self.session_token,
            "AppKey": self.app_key
        }
        customerDetailsResponse = self._getRequest("api.customer.details", params)
        return customerDetailsResponse

    def getHolding(self):
        params = {}
        holdingResponse = self._getRequest("api.holding", params)
        return holdingResponse

    def _getStockCodeFromOrder(self, order: Order):
        pass

    def _getExchangeCodeFromOrder(self, order: Order):
        """Convert the exchange code to the format required by the broker's API.
            :returns 'NSE' for NSE, 'BSE' for BSE, 'NFO' for NFO, None otherwise"""
        if order.exchange == "NSE":
            return "NSE"
        elif order.exchange == "BSE":
            return "BSE"
        elif order.exchange == "NFO":
            return "NFO"
        else:
            return None

    def _getProductFromOrder(self, order: Order):
        """Convert the segment to the format required by the broker's API.
            :returns 'cash' for EQUITY or CASH, None otherwise"""
        if order.segment == "EQUITY" or order.segment == "CASH":
            return "cash"
        else:
            return None

    def _getActionFromOrder(self, order: Order):
        if order.transactionType == "BUY":
            return "buy"
        elif order.transactionType == "SELL":
            return "sell"
        else:
            return None

    def _getOrderTypeFromOrder(self, order: Order):
        if order.orderType == "LIMIT":
            return "limit"
        elif order.orderType == "MARKET":
            return "market"
        else:
            return None

    def _getValidityFromOrder(self, order: Order):
        if order.duration == "DAY":
            return "day"
        elif order.duration == "IOC":
            return "ioc"
        else:
            return None

    def placeOrder(self, order: Order):
        params = {
            "stock_code": self._getStockCodeFromOrder(order),
            "exchange_code": self._getExchangeCodeFromOrder(order),
            "product": self._getProductFromOrder(order),
            "action": self._getActionFromOrder(order),
            "order_type": self._getOrderTypeFromOrder(order),
            "stoploss": str(order.stopLossPrice),
            "quantity": str(order.quantity),
            "price": str(order.price),
            "validity": self._getValidityFromOrder(order),
            # "validity_date": None,
            "disclosed_quantity": str(order.discQuantity)
        }
        response = self._postRequest("api.order.place", params)

        if response is not None and response.get('status', False):
            return response
        else:
            logger.error(f"API request failed: {response}")
        return None