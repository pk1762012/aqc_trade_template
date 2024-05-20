from angelone.angelone import AngelOne
import pyotp

tokens = {
    "jwtToken": None,
    "refreshToken": None,
    "feedToken": None
}

def save_tokens(jwt, refresh, feed):
    tokens["jwtToken"] = jwt
    tokens["refreshToken"] = refresh
    tokens["feedToken"] = feed

class TradingLogic:
    def __init__(self, apiKey, client_code, password, qrValue):
        self.apiKey = apiKey
        self.client_code = client_code
        self.password = password
        self.qrValue = qrValue
        self.angel_one = None

    def login(self):
        try:
            if not all([self.apiKey, self.client_code, self.password, self.qrValue]):
                return {"status": False, "message": "Missing required authentication details"}

            self.angel_one = AngelOne(api_key=self.apiKey)
            totp = pyotp.TOTP(self.qrValue).now()
            result = self.angel_one.generateSession(self.client_code, self.password, totp)

            if result['status']:
                save_tokens(result['data']['jwtToken'], result['data']['refreshToken'], result['data']['feedToken'])
            return result
        except Exception as e:
            return {"status": False, "message": str(e)}

    def orders(self):
        if self.angel_one is None:
            return {"status": False, "message": "AngelOne instance not initialized. Please login first."}
        return self.angel_one.getOrderBook()

def main():
    apiKey = 'dWjWcggF'
    client_code = 'R58905663'
    password = '9778'
    qrValue = '3VQAGA5NST45MMDRBHC6LCVA6U'

    trading_logic = TradingLogic(apiKey, client_code, password, qrValue)
    login_response = trading_logic.login()
    if login_response['status']:
        order_book = trading_logic.orders()
        print("Order Book:", order_book)
    else:
        print("Login failed:", login_response['message'])

if __name__ == "__main__":
    main()
