import unittest
from angelone import angelone, totp
from body.Order import Order

class TestAngelOne(unittest.TestCase):

    orderId = None
    @classmethod
    def setUpClass(cls):
        cls.angelone = angelone.AngelOne(api_key="HZfHSjFN")
        data = cls.angelone.generateSession("ALNL1030","2703",totp.getTotp())
        cls.refreshToken = data['data']['refreshToken']

    def test_getProfile(self):
        res = self.angelone.getProfile(self.refreshToken)
        self.assertEqual(res['status'], True)

    def test_placeOrder(self):
        orderNew = Order("NSE", "EQUITY", 100.0, "BUY", 1, 0, 0.0, "SBIN", "NORMAL", "LIMIT", "DELIVERY", "DAY")
        res = self.angelone.placeOrder(orderNew)
        self.assertEqual(res['status'], True)

    def test_modifyOrder(self):
        orderNew = Order("NSE", "EQUITY", 100.0, "BUY", 1, 0, 0.0, "SBIN", "NORMAL", "LIMIT", "DELIVERY", "DAY")
        res = self.angelone.placeOrder(orderNew)
        orderId = res['data']['orderid']
        orderMod = Order("NSE", "EQUITY", 89.0, "BUY", 1, 0, 0.0, "SBIN", "NORMAL", "LIMIT", "DELIVERY", "DAY")
        resMod = self.angelone.modifyOrder(orderMod, orderId)
        self.assertEqual(resMod['status'], True)

    def test_cancelOrder(self):
        orderNew = Order("NSE", "EQUITY", 100.0, "BUY", 1, 0, 0.0, "SBIN", "NORMAL", "LIMIT", "DELIVERY", "DAY")
        res = self.angelone.placeOrder(orderNew)
        orderId = res['data']['orderid']
        res = self.angelone.cancelOrder("NORMAL", orderId)
        self.assertEqual(res['status'], True)

    def test_getOrderBook(self):
        res = self.angelone.getOrderBook()
        self.assertEqual(res['status'], True)

    def test_getTradeBook(self):
        res = self.angelone.getTradeBook()
        self.assertEqual(res['status'], True)

    def test_getHolding(self):
        res = self.angelone.getHolding()
        self.assertEqual(res['status'], True)


if __name__ == '__main__':
    unittest.main()