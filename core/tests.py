from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from core.models import Currency

class CurrencyCommandTest(TestCase):
    def test_load_currencies_command(self):
        out = StringIO()
        call_command('load_currencies', stdout=out)
        
        currencies = Currency.objects.all()
        self.assertTrue(currencies.exists())
        
        default_currency = Currency.objects.filter(is_default=True).first()
        self.assertIsNotNone(default_currency)
        
        self.assertTrue(Currency.objects.filter(code='USD').exists())
        self.assertTrue(Currency.objects.filter(code='EUR').exists())
        
        self.assertIn('Successfully loaded currencies', out.getvalue())
        
    def test_default_currency_getter(self):
        Currency.objects.all().delete()
        
        test_currency = Currency.objects.create(
            code='XYZ',
            name='Test Currency',
            symbol='T',
            is_default=True
        )
        
        default = Currency.get_default()
        self.assertEqual(default, test_currency)
        
        test_currency.is_default = False
        test_currency.save()
        
        default = Currency.get_default()
        self.assertEqual(default, test_currency)
