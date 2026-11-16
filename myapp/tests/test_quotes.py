from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from myapp.models import StockInfo


class LiveQuoteTests(TestCase):
    def setUp(self):
        StockInfo.objects.create(name="LIVE", company_name="Live Inc", stock_price=10.0)

    def test_stale_price_is_refreshed_once_and_shared(self):
        with mock.patch("myapp.pipeline.quotes.fetch_quote", return_value=12.34) as fetch:
            first = self.client.get("/api/quote", {"text": "live"}).json()
            second = self.client.get("/api/quote", {"text": "LIVE"}).json()
        self.assertEqual((first["price"], second["price"]), (12.34, 12.34))
        self.assertEqual(fetch.call_count, 1)  # the second visitor gets the shared price
        self.assertEqual(StockInfo.objects.get(name="LIVE").stock_price, 12.34)

    def test_price_older_than_a_minute_is_fetched_again(self):
        StockInfo.objects.filter(name="LIVE").update(price_updated_at=timezone.now() - timedelta(minutes=2))
        with mock.patch("myapp.pipeline.quotes.fetch_quote", return_value=11.0) as fetch:
            data = self.client.get("/api/quote", {"text": "LIVE"}).json()
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(data["price"], 11.0)

    def test_failed_lookup_keeps_the_stored_price(self):
        with mock.patch("myapp.pipeline.quotes.fetch_quote", return_value=None):
            data = self.client.get("/api/quote", {"text": "LIVE"}).json()
        self.assertEqual(data["price"], 10.0)

    def test_unknown_ticker(self):
        self.assertEqual(self.client.get("/api/quote", {"text": "NOPE"}).status_code, 404)
