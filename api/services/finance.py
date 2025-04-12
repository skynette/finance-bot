from api.schemas import CommandResponse
from core.models import Category, Expense, get_default_currency, Income, User
from asgiref.sync import sync_to_async

class FinanceService:
    @staticmethod
    async def handle_add_income_command(args: list, user_id: int) -> CommandResponse:
        error_message = (
        """❌ Invalid format for `/add_income` command.
        Usage: `/add_income [amount] [category] [description (optional)]`
        Example: `/add_income 200 Salary Monthly paycheck`
        """
        )

        if not args or len(args) < 2:
            return CommandResponse(
                status="error",
                details={"message": error_message}
            )

        amount_str = args[0]
        category_name = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            return CommandResponse(
                status="error",
                details={"message": error_message}
            )

        record_data = {
            "amount": amount,
            "category_name": category_name,
            "description": description
        }

        user_id = await User.objects.aget(telegram_id=user_id)
        response = await FinanceService.create_income(record_data, user_id.id)
        
        if response.status == "success":
            response.details["message"] = (
                f"✅ Income of {response.details['currency']}{amount} has been recorded under '{category_name}'."
            )
        else:
            response.details["message"] = (
                f"❌ Failed to record income: {response.details.get('detail', 'Unknown error.')}"
            )

        return response
    
    
    @staticmethod
    async def handle_add_expense_command(args: list, user_id: int) -> CommandResponse:
        error_message = (
        """❌ Invalid format for `/add_expense` command.
        Usage: `/add_expense [amount] [category] [description (optional)]`
        Example: `/add_expense 150 Groceries Weekly food shopping`
        """
        )

        if not args or len(args) < 2:
            return CommandResponse(status="error", details={"message": error_message})

        amount_str = args[0]
        category_name = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            return CommandResponse(status="error", details={"message": error_message})

        record_data = {
            "amount": amount,
            "category_name": category_name,
            "description": description,
        }

        user = await User.objects.aget(telegram_id=user_id)
        response = await FinanceService.create_expense(record_data, user.id)

        if response.status == "success":
            response.details["message"] = (
                f"💸 Expense of {response.details['currency']}{amount} has been recorded under '{category_name}'."
            )
        else:
            response.details["message"] = (
                f"❌ Failed to record expense: {response.details.get('detail', 'Unknown error.')}"
            )

        return response
    
          
    @staticmethod
    async def create_income(record_data: dict, user_id: int) -> CommandResponse:
        try:
            user = await User.objects.aget(id=user_id)

            category, _ = await Category.objects.aget_or_create(
                user=user,
                name=record_data["category_name"],
                defaults={'is_active': True}
            )
            
            currency = await sync_to_async(get_default_currency)()
            
            income = await Income.objects.acreate(
                user=user,
                amount=record_data["amount"],
                category=category,
                currency=currency,
                description=record_data.get("description", "")
            )
            
            return CommandResponse(
                status="success",
                details={
                    "type": "income",
                    "amount": record_data["amount"],
                    "category": category.name,
                    "currency": currency.code,
                }
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
            user = await User.objects.aget(id=user_id)

            category, _ = await sync_to_async(Category.objects.get_or_create)(
                user=user,
                name=record_data["category_name"],
                defaults={'is_active': True}
            )
            
            currency = await sync_to_async(get_default_currency)()

            expense = await Expense.objects.acreate(
                user=user,
                amount=record_data["amount"],
                category=category,
                currency=currency,
                description=record_data.get("description", "")
            )

            return CommandResponse(
                status="success",
                details={
                    "type": "expense",
                    "amount": expense.amount,
                    "category": category.name,
                    "currency": currency.code
                }
            )

        except Exception as e:
            print("Error creating expense:", str(e))
            return CommandResponse(status="error", details={"detail": str(e)})
