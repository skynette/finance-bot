from core.models import Currency

async def seed_currencies():
    currencies = [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "NGN", "name": "Naira", "symbol": "₦"},
    ]
    
    for currency in currencies:
        await Currency.objects.aupdate_or_create(
            code=currency["code"],
            defaults=currency
        )