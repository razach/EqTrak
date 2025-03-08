from django.test import TestCase
from market_data.services import MarketDataService

class MarketDataBasicTest(TestCase):
    def test_get_security(self):
        """Test retrieving a security"""
        # This will create a security if it doesn't exist
        security = MarketDataService.get_or_create_security('AAPL')
        self.assertEqual(security.symbol, 'AAPL')
        self.assertIsNotNone(security.name)
        
    def test_get_latest_price(self):
        """Test retrieving latest price"""
        price_data = MarketDataService.get_latest_price('AAPL')
        self.assertIn('date', price_data)
        self.assertIn('price', price_data)
        self.assertIn('is_stale', price_data)
        
    def test_get_price_history(self):
        """Test retrieving price history"""
        history = MarketDataService.get_price_history('MSFT', days=30)
        self.assertTrue(len(history) > 0)
        self.assertIn('date', history[0])
        self.assertIn('close', history[0])
