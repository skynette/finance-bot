from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Currency

class Command(BaseCommand):
    help = 'Loads default currencies into the database'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        default_currencies = [
            {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦', 'is_default': True},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_default': False},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_default': False},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_default': False},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'is_default': False},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'is_default': False},
            {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'is_default': False},
            {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'Fr', 'is_default': False},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'is_default': False},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'is_default': False},
            {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽', 'is_default': False},
            {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$', 'is_default': False},
            {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩', 'is_default': False},
            {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'is_default': False},
            {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$', 'is_default': False},
        ]

        created_count = 0
        updated_count = 0
        
        existing_default = Currency.objects.filter(is_default=True).first()
        
        for currency_data in default_currencies:
            currency, created = Currency.objects.update_or_create(
                code=currency_data['code'],
                defaults={
                    'name': currency_data['name'],
                    'symbol': currency_data['symbol'],
                    'is_default': currency_data['is_default'] and not existing_default
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created currency: {currency}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated currency: {currency}")
                
        if not Currency.objects.filter(is_default=True).exists():
            ngn = Currency.objects.filter(code='NGN').first()
            if ngn:
                ngn.is_default = True
                ngn.save()
                self.stdout.write(self.style.SUCCESS(f"Set {ngn.code} as default currency"))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded currencies: {created_count} created, {updated_count} updated'
        ))