from angelone.angelOne_scrip_master import get_token_id_from_symbol

class MockOrder:
    def __init__(self, tradingSymbol, segment, exchange):
        self.tradingSymbol = tradingSymbol
        self.segment = segment
        self.exchange = exchange

def _getSymbolToken(order):
    formatted_symbol = _getTradingSymbolFromOrder(order)
    print(f'Formatted symbol from other function: {formatted_symbol}')
    token = get_token_id_from_symbol(formatted_symbol, order.exchange)
    return str(token)

def _getTradingSymbolFromOrder(order):
    if order.segment == "EQUITY":
        return order.tradingSymbol + "-EQ"
    else:
        return order.tradingSymbol

mock_order = MockOrder("IRFC", "EQUITY", "NSE")

formatted_symbol = _getTradingSymbolFromOrder(mock_order)
print("Formatted Trading Symbol:", formatted_symbol)

symbol_token = _getSymbolToken(mock_order)
print("Symbol Token:", symbol_token)
