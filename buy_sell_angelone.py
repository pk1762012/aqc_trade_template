from collections import defaultdict
from angelone.angelone import AngelOne, Order

class TradingLogic:
    def __init__(self, api_key=None, access_token=None):
        self.api_key = api_key
        self.access_token = access_token
        angel_one = AngelOne(api_key=api_key, access_token=access_token)
        self.angel_one = angel_one
    
    def orders(self):
        return self.angel_one.getOrderBook()

    def reformat_order_book(self, orders, trades):
        symbols_in_trades = {trade["Symbol"] for trade in trades}  
        successful_trades = set()
        failed_trades = []

        for order in orders.get("data", []):
            symbol = order["tradingsymbol"].split("-")[0]
            if symbol not in symbols_in_trades:
                continue  
            status = order["orderstatus"].lower()
            reason = order.get("text", "No specific error provided")
            if "complete" in status:
                successful_trades.add(symbol) 
            else:
                failed_trades.append(f"{symbol} due to {reason}")

        success_message = f"[{', '.join(successful_trades) if successful_trades else 'None'}]"
        failure_message = "/n".join(failed_trades) if failed_trades else "None"
        final_message = f"Successfully placed {success_message} / Failed in {failure_message}"

        results = []
        for trade in trades:
            trade_symbol = trade["Symbol"]
            matching_order = next((order for order in orders.get("data", []) if trade_symbol == order["tradingsymbol"].split("-")[0]), None)
            if matching_order: 
                simplified_order_details = {
                    "averageprice": matching_order.get("averageprice", ""),
                    "orderupdatetime": matching_order.get("exchorderupdatetime", ""),
                    "filledshares": matching_order.get("filledshares", ""),
                    "unfilledshares": matching_order.get("unfilledshares", ""),
                    "lotsize": matching_order.get("lotsize", ""),
                    "optiontype": matching_order.get("optiontype", ""),
                    "instrumenttype": matching_order.get("instrumenttype", ""),
                    "orderid" : matching_order.get("orderid", ""),
                    "orderstatus": matching_order.get("orderstatus", ""),
                    "ordertype": matching_order.get("ordertype", ""),
                    "tradingsymbol": matching_order.get("tradingsymbol", ""),
                    "transactiontype": matching_order.get("transactiontype", ""),
                    "delivery_intraday": matching_order.get("producttype", "")
                }
                trade_details = {
                    "advice_status": order.get("orderstatus", "Unknown"),
                    "stock_symbol": trade_symbol,
                    "Type": trade["Type"],
                    "stock_user_qty": trade["Quantity"],
                    "stock_user_price": trade["Price"],
                    "order_details": simplified_order_details              
                }
                results.append(trade_details)
            else:
                trade_details = {
                    "advice_status": "No matching order found",
                    "stock_symbol": trade_symbol,
                    "Type": trade["Type"],
                    "stock_user_qty": trade["Quantity"],
                    "stock_user_price": trade["Price"],
                    "order_details": None
                }
                results.append(trade_details) 
                           
        return {
            "final_message": final_message,
            "trade_details": results
        }

    def process_trades(self, trades):
        if trades is None:
            return {"error": "No trades provided"}, 400

        results = []
        trades_by_user = defaultdict(list)
        for trade in trades:
            trades_by_user[trade['user_email']].append(trade)

        try:
            for user_email, user_trades in trades_by_user.items():
                sell_trades = sorted((trade for trade in user_trades if trade['Type'] == 'SELL'), key=lambda x: x.get('Priority', float('inf')))
                buy_trades = sorted((trade for trade in user_trades if trade['Type'] == 'BUY'), key=lambda x: x.get('Priority', float('inf')))

                sold_successfully, not_sold_stocks = self.process_sell_orders(sell_trades)
                if not sold_successfully:
                    for stock in not_sold_stocks:
                        failure_result = self.trigger_failure_flow(user_email, sell_trades, stock['error'])
                        results.append(failure_result)
                    continue 

                bought_successfully, not_bought_stocks = self.process_buy_orders(buy_trades)
                if not bought_successfully:
                    for stock in not_bought_stocks:
                        partial_success_result = self.trigger_partial_success_flow(user_email, [stock])
                        results.append(partial_success_result)
                else:
                    success_result = self.trigger_success_flow(user_email, user_trades)
                    results.append(success_result)

            orders_after = self.orders()
            reformat_result = self.reformat_order_book(orders_after, trades)

            return {
                "results": results,
                "order_book": reformat_result
            }
        except Exception as error:
            return {"error from buy_sell": str(error)}, 500
            
        
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
                    not_sold_stocks.append({"trading_symbol": trade['Symbol'], "error_process_sell": order_result.get('error', 'Unknown error')})
            except Exception as e:
                error_message = f"while processing sell order, there is an issue with payload OR processing payload info OR it is past trading hours - {str(e)}"
                not_sold_stocks.append({"trading_symbol": trade['Symbol'], "error": error_message})
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
                    not_bought_stocks.append({"trading_symbol": trade['Symbol'], "error_process_buy": order_result.get('error', 'Unknown error')})
            except Exception as e:
                error_message = f"while processing buy order, there is an issue with payload OR processing payload info OR it is past trading hours - {str(e)}"
                not_bought_stocks.append({"trading_symbol": trade['Symbol'], "error": error_message})
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
