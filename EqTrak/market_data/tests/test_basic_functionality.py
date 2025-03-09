from django.test import TestCase
from market_data.services import MarketDataService
import unittest

class BasicFunctionalityTests(unittest.TestCase):
    
    def test_get_security(self):
        """Test that we can retrieve a security by symbol"""
        security = MarketDataService.get_or_create_security('AAPL', user=None)
        self.assertEqual(security.symbol, 'AAPL')
        self.assertEqual(security.name, 'Apple Inc.')
    
    def test_get_latest_price(self):
        """Test that we can retrieve the latest price for a security"""
        price_data = MarketDataService.get_latest_price('AAPL', user=None)
        self.assertIn('price', price_data)
        self.assertIsInstance(price_data['price'], (int, float))
    
    def test_get_history(self):
        """Test that we can retrieve price history"""
        history = MarketDataService.get_price_history('MSFT', days=30, user=None)
        self.assertTrue(len(history) > 0)
        self.assertIn('close', history[0])
