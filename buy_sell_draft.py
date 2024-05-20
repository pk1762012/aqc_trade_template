from pymongo import MongoClient
from datetime import datetime, timezone
from collections import defaultdict
import pandas as pd
from angelone.angelone import AngelOne, Order

class DatabaseClient:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client['test_quark']

    def get_trades_for_today(self):
        return self.db.trade_orders.find()

    def update_trade_status(self, trade_id, status, additional_info=None):
        update_doc = {"$set": {"trade_place_status": status}}
        if additional_info:
            update_doc["$set"].update(additional_info)
        self.db.trade_orders.update_one({"_id": trade_id}, update_doc)

    def log_advisor_notice(self, advisor_email, message):
        self.db.advisor_notices.insert_one({
            "advisor_email": advisor_email,
            "message": message,
            "date": datetime.now(timezone.utc)
        })

    def get_user_portfolio(self, user_email):
        cursor = self.db.trade_orders.find({"Client_identifier": user_email, "advise.Type": "SELL"})
        portfolio = {}
        for entry in cursor:
            key = (entry['advise']['Symbol'], entry['advise']['Priority'], entry['advise']['Place order trigger date'])
            if key in portfolio:
                portfolio[key] += entry['advise']['Quantity']
            else:
                portfolio[key] = entry['advise']['Quantity']
        return portfolio

    def load_trades_from_csv(self, file_path):
        try:
            data = pd.read_csv(file_path)
            for _, row in data.iterrows():
                client_identifier = row['Client_identifier']
                advise = row.to_dict()
                advise.pop('Client_identifier')
                self.db.trade_orders.insert_one({"Client_identifier": client_identifier, "advise": advise})
        except Exception as error:
            print(error)

class TradingLogic:
    def __init__(self, db_client, available_balance):
        self.db_client = db_client
        self.available_balance = available_balance

    def update_balance(self, amount):
        self.available_balance += amount
        print(f"Updated Balance: {self.available_balance}")

    def process_trades(self, customer_confirms):
        if not customer_confirms:
            print("Trade canceled by customer.")
            return

        if not self.client_login():
            print("Client login failed.")
            return

        trades = list(self.db_client.get_trades_for_today())
        trades.sort(key=lambda x: (x['advise']['Place order trigger date'], x['advise']['Priority']))

        trades_by_user = defaultdict(list)
        for trade in trades:
            trades_by_user[trade['Client_identifier']].append(trade)

        for user_email, trades in trades_by_user.items():
            sell_trades = [trade for trade in trades if trade['advise']['Type'] == 'SELL']
            if not self.process_sell_orders(sell_trades):
                self.trigger_failure_flow(user_email, sell_trades, "Insufficient sell quantity")
            else:
                buy_trades = [trade for trade in trades if trade['advise']['Type'] == 'BUY']
                successfully_bought, not_bought_stocks = self.process_buy_orders(user_email, buy_trades)
                if successfully_bought:
                    self.trigger_success_flow(user_email, trades)
                else:
                    self.trigger_partial_success_flow(user_email, not_bought_stocks)

    def client_login(self):
        return True

    def process_sell_orders(self, trades):
        for trade in trades:
            if not self.check_sell_quantity(trade):
                return False
            else:
                revenue = self.get_trade_cost(trade['advise']['Symbol']) * trade['advise']['Quantity']
                self.update_balance(revenue)
                self.db_client.update_trade_status(trade['_id'], 'executed')
        return True

    def process_buy_orders(self, user_email, trades):
        not_bought_stocks = []
        for trade in trades:
            cost = self.get_trade_cost(trade['advise']['Symbol']) * trade['advise']['Quantity']
            if not self.can_afford_trade(cost):
                not_bought_stocks.append(trade['advise']['Symbol'])
                self.db_client.update_trade_status(trade['_id'], 'partial_success')
            else:
                self.update_balance(-cost)
                self.db_client.update_trade_status(trade['_id'], 'executed')
        return len(not_bought_stocks) == 0, not_bought_stocks

    def check_sell_quantity(self, trade):
        portfolio = self.db_client.get_user_portfolio(trade['Client_identifier'])
        key = (trade['advise']['Symbol'], trade['advise']['Priority'], trade['advise']['Place order trigger date'])
        available_qty = portfolio.get(key, 0)
        return available_qty >= int(trade['advise']['Quantity'])

    def can_afford_trade(self, cost):
        return self.available_balance >= cost

    def get_trade_cost(self, symbol):
        prices = {'ETF1': 5000, 'ETF2': 10000, 'ETF3': 15000, 'ETF4': 20000}
        return prices.get(symbol, 0)

    def trigger_failure_flow(self, user_email, trades, reason):
        advisor_email = (trades[0].get('trade_given_by') if trades else 'no_advisor@company.com')
        for trade in trades:
            self.db_client.update_trade_status(trade['_id'], 'failed', {"failure_reason": reason})
        
        failed_stocks = [trade['advise']['Symbol'] for trade in trades]
        message = f"The order was not executed as the available quantity for {', '.join(failed_stocks)} was lower than prescribed sell. Contact your advisor/RM for resolving this."
        self.db_client.log_advisor_notice(advisor_email, message)
        print(message)

    def trigger_success_flow(self, user_email, trades):
        for trade in trades:
            self.db_client.update_trade_status(trade['_id'], 'success')
        success_message = "All the recommendations of the advisor have been placed."
        self.db_client.log_advisor_notice(trades[0]['trade_given_by'], success_message)
        print(f"Success: {success_message} for {user_email}")

    def trigger_partial_success_flow(self, user_email, not_bought_stocks):
        message = f"{', '.join(not_bought_stocks)} did not get bought today, please connect with your advisor/RM."
        print(f"Partial Success: {message} for {user_email}")

def main():
    db_client = DatabaseClient("mongodb://localhost:27017/")
    db_client.load_trades_from_csv("Stock_Trades_Data.csv")  # Specify the correct path to your CSV file
    available_balance = 50000
    trading_logic = TradingLogic(db_client, available_balance)
    
    customer_confirms = True
    trading_logic.process_trades(customer_confirms)

if __name__ == "__main__":
    main()
