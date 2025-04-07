from api.schemas import CommandResponse
from core.models import Income, Expense, Currency, Category
from django.db import transaction
from typing import Optional

class FinanceService:
    @staticmethod
    async def create_income(record_data: dict, user_id: int) -> CommandResponse:
        try:
            async with transaction.atomic():
                currency = await Currency.objects.aget(code=record_data["currency_code"])
                category, _ = await Category.objects.aget_or_create(
                    user_id=user_id,
                    name=record_data["category_name"],
                    defaults={'is_active': True}
                )
                
                income = await Income.objects.acreate(
                    user_id=user_id,
                    amount=record_data["amount"],
                    currency=currency,
                    category=category,
                    description=record_data.get("description", "")
                )
                
                return CommandResponse(
                    status="success",
                    details={
                        "type": "income",
                        "amount": income.amount,
                        "currency": currency.code,
                        "category": category.name
                    }
                )
        except Currency.DoesNotExist:
            print("Currency not found")
            return CommandResponse(
                status="error",
                details={"detail": f"Currency {record_data['currency_code']} not found"}
            )
        except Exception as e:
            print("Error creating income:", str(e))
            return CommandResponse(
                status="error",
                details={"detail": str(e)}
            )

    @staticmethod
    async def create_expense(record_data: dict, user_id: int) -> CommandResponse:
        try:
            async with transaction.atomic():
                currency = await Currency.objects.aget(code=record_data["currency_code"])
                category, _ = await Category.objects.aget_or_create(
                    user_id=user_id,
                    name=record_data["category_name"],
                    defaults={'is_active': True}
                )
                
                expense = await Expense.objects.acreate(
                    user_id=user_id,
                    amount=record_data["amount"],
                    currency=currency,
                    category=category,
                    description=record_data.get("description", "")
                )
                
                return CommandResponse(
                    status="success",
                    details={
                        "type": "expense",
                        "amount": expense.amount,
                        "currency": currency.code,
                        "category": category.name
                    }
                )
        except Currency.DoesNotExist:
            print("Currency not found")
            return CommandResponse(
                status="error",
                details={"detail": f"Currency {record_data['currency_code']} not found"}
            )
        except Exception as e:
            print("Error creating expense:", str(e))
            return CommandResponse(
                status="error",
                details={"detail": str(e)}
            )