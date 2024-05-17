from pymongo import MongoClient

def insert_documents():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['test_quark']  
    collection = db['trade_orders'] 

    documents = [
        {"user_email": "2015ravimishra@gmail.com", "Type": "SELL", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF1", "Quantity": 10, "Priority": 0, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "SELL", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF2", "Quantity": 11, "Priority": 0, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF3", "Quantity": 10, "Priority": 1, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF4", "Quantity": 5, "Priority": 2, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF4", "Quantity": 5, "Priority": 1, "Place_order_trigger_date": "T1", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "SELL", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF1", "Quantity": 10, "Priority": 0, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "SELL", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF2", "Quantity": 11, "Priority": 0, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF3", "Quantity": 10, "Priority": 1, "Place_order_trigger_date": "T0", "trade_given_by": "advisor@company.com"},
        {"user_email": "2015ravimishra@gmail.com", "Type": "BUY", "Exchange": "NSE", "Segment": "CASH", "Product_Type": "DELIVERY", "Order_type": "MARKET", "Price": 0, "Symbol": "ETF4", "Quantity": 10, "Priority": 1, "Place_order_trigger_date": "T1", "trade_given_by": "advisor@company.com"}
    ]

    collection.insert_many(documents)
    print("Documents inserted successfully.")

if __name__ == "__main__":
    insert_documents()
