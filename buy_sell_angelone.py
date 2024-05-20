from collections import defaultdict
from angelone.angelone import AngelOne, Order
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
    def __init__(self, apiKey=None, client_code=None, password=None, qrValue=None):
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
            print(result)
            return result
        except Exception as e:
            return {"status": False, "message": str(e)}

        
    def available_funds(self):
        return self.angel_one.getFunds()
    
    def orders(self):
        return self.angel_one.getOrderBook()
    
    def logout(self, client_code):
        if self.angel_one and client_code:
            logout_response = self.angel_one.terminateSession(client_code)
            print("Logout response:", logout_response)
            return logout_response
        return {"status": False, "message": "No active session or missing client code"}
    
    def reformat_order_book(self, orders, trades):
        symbols_in_trades = {trade["Symbol"] for trade in trades}  # Collect all symbols from payload trades
        successful_trades = []
        failed_trades = []

        # Process orders to categorize them into successful and failed trades, only if they are in the payload
        for order in orders.get("data", []):
            symbol = order["tradingsymbol"].split("-")[0]
            if symbol not in symbols_in_trades:
                continue  # Skip processing this order if the symbol is not in the provided trades
            status = order["orderstatus"].lower()
            reason = order.get("text", "No specific error provided")
            if "success" in status:
                successful_trades.append(symbol)
            else:
                failed_trades.append(f"{symbol} due to {reason}")

        # Format the final message
        success_message = f"[{', '.join(successful_trades) if successful_trades else 'None'}]"
        failure_message = "/n".join(failed_trades) if failed_trades else "None"
        final_message = f"Successfully placed {success_message} / Failed in {failure_message}"

        results = []
        for trade in trades:
            trade_details = {
                "stock_symbol": trade["Symbol"],
                "Type": trade["Type"],
                "stock_user_qty": trade["Quantity"],
                "stock_user_price": trade["Price"],
                "advice_status": self.extract_trade_response(trade["Symbol"], orders)
            }
            results.append(trade_details)

        return {
            "final_message": final_message,
            "trade_details": results
        }

    def extract_trade_response(self, symbol, orders):
        for order in orders.get("data", []):
            if symbol in order["tradingsymbol"].split("-")[0]:
                return {
                    "order_details": order,
                    "status": order.get("orderstatus", "Unknown"),
                }
        return {"status": "Not found", "error_message": "No matching order found"}



    def process_trades(self, trades):
    
        login_response = self.login()
        if not login_response['status']:
            return {"status": False, "message": "Login failed, cannot process trades."}
        
        funds_before = self.available_funds()

        trades.sort(key=lambda x: x['Priority'])

        trades_by_user = defaultdict(list)
        for trade in trades:
            trades_by_user[trade['user_email']].append(trade)

        results = []
        try:
            for user_email, user_trades in trades_by_user.items():
                sell_trades = [trade for trade in user_trades if trade['Type'] == 'SELL']
                sold_successfully, not_sold_stocks = self.process_sell_orders(sell_trades)

                if len(not_sold_stocks) == len(sell_trades):
                    for stock in not_sold_stocks:
                        failure_result = self.trigger_failure_flow(user_email, sell_trades, stock['error'])
                        results.append(failure_result)
                    continue 

                buy_trades = [trade for trade in user_trades if trade['Type'] == 'BUY']
                bought_successfully, not_bought_stocks = self.process_buy_orders(buy_trades)
                if not bought_successfully:
                    for stock in not_bought_stocks:
                        partial_success_result = self.trigger_partial_success_flow(user_email, [stock])
                        results.append(partial_success_result)
                else:
                    success_result = self.trigger_success_flow(user_email, user_trades)
                    results.append(success_result)


            funds_after = self.available_funds()
            orders_after = self.orders()
            reformat_result = self.reformat_order_book(orders_after, trades)

            return {
                "results": results,
                "funds_before_trade": funds_before,
                "funds_after_trade": funds_after,
                "order_book": reformat_result
            }
        finally:
            self.logout(self.client_code)
        

    def process_sell_orders(self, trades):
        not_sold_stocks = []
        for trade in trades:
            try:
                order = Order(
                    segment=trade['Segment'],  
                    tradingSymbol=trade['Symbol'],  
                    transactionType="SELL",
                    exchange=trade['Exchange'],
                    orderType=trade['Order_type'],
                    productType=trade.get('productType', "MARKET"),
                    duration="DAY",  
                    price=trade['Price'],
                    quantity=trade['Quantity'],
                    stopLossPrice=trade.get('StopLossPrice', "0.0")
                )
                order_result = self.angel_one.placeOrder(order)
                if not order_result or 'status' not in order_result or not order_result['status']:
                    not_sold_stocks.append({"trading_symbol": trade['Symbol'], "error": order_result.get('error', 'Unknown error')})
            except Exception as e:
                not_sold_stocks.append({"trading_symbol": trade['Symbol'], "error": str(e)})
        if not_sold_stocks:
            return False, not_sold_stocks
        return True, []

    def process_buy_orders(self, trades):
        not_bought_stocks = []
        for trade in trades:
            try:
                order = Order(
                    segment=trade['Segment'],
                    tradingSymbol=trade['Symbol'],  
                    transactionType="BUY",
                    exchange=trade['Exchange'],
                    orderType=trade['Order_type'],
                    productType=trade.get('productType', "MARKET"),
                    duration="DAY",
                    price=trade['Price'],
                    quantity=trade['Quantity'],
                    stopLossPrice=trade.get('StopLossPrice', "0.0")
                )
                order_result = self.angel_one.placeOrder(order)
                if not order_result or 'status' not in order_result or not order_result['status']:
                    not_bought_stocks.append({"trading_symbol": trade['Symbol'], "error": order_result.get('error', 'Unknown error')})
            except Exception as e:
                not_bought_stocks.append({"trading_symbol": trade['Symbol'], "error": str(e)})
        if not_bought_stocks:
            return False, not_bought_stocks
        return True, []
    
    def trigger_success_flow(self, user_email, trades):
        return {"status": "success", "user": user_email, "message": "All recommendations have been sent to AngelOne."}

    def trigger_partial_success_flow(self, user_email, not_bought_stocks):
        return {"status": "partial_success", "user": user_email, "not_bought_stocks": not_bought_stocks}

    def trigger_failure_flow(self, user_email, trades, reason):
        return {"status": "failure", "user": user_email, "reason": reason}


if __name__ == "__main__":
    trades = [
        {"user_email": "2015ravimishra@gmail.com", "Type": "SELL", "Exchange": "NSE", "Segment": "EQUITY", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "NIF100BEES", "Quantity": 10, "Priority": 0, "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "EQUITY", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "AUTOBEES", "Quantity": 10, "Priority": 1, "trade_given_by": "advisor@company.com"},
    ]
    trading_logic = TradingLogic()
    results = trading_logic.process_trades(trades)
    print(results)
