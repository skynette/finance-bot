from fastapi import APIRouter, Request, HTTPException
from api.services import TelegramService, FinanceService
import json

router = APIRouter()
telegram_service = TelegramService()

@router.post("/telegram-webhook")
async def handle_webhook(request: Request):
    print("Received webhook request")
    try:
        update_data = await request.json()
        result = await telegram_service.process_update(update_data)
        
        if not result.chat_id:
            return {"status": "ok"}  # No chat to reply to
        
        # Handle different command types
        if result.status == "income_command":
            finance_result = await FinanceService.create_income(
                result.details["record"],
                1
            )
            await telegram_service._send_message(
                result.chat_id,
                f"✅ Income recorded: {finance_result.details['amount']} {finance_result.details['currency']}"
            )
        elif result.status == "expense_command":
            finance_result = await FinanceService.create_expense(
                result.details["record"],
                1
            )
            await telegram_service._send_message(
                result.chat_id,
                f"✅ Expense recorded: {finance_result.details['amount']} {finance_result.details['currency']}"
            )
        elif result.status == "help_command":
            help_text = """
                        📚 *Available Commands*:

                        */add_income* [amount] [currency] [category]
                        Example: `/add_income 100 USD Salary`
                        Record a new income transaction

                        */add_expense* [amount] [currency] [category]  
                        Example: `/add_expense 50 EUR Groceries`
                        Record a new expense

                        */help* - Show this help message
                    """
            await telegram_service._send_message(
                result.chat_id,
                help_text
            )
        elif result.status == "unrecognized_command":
            await telegram_service._send_message(
                result.chat_id,
                "❌ Unrecognized command. Send /help to see available commands."
            )
        elif result.status == "message_received":
            await telegram_service._send_message(
                result.chat_id,
                "ℹ️ Send /help to see available commands."
            )
        elif result.status == "error":
            await telegram_service._send_message(
                result.chat_id,
                f"❌ Error: {result.details.get('detail', 'Unknown error')}"
            )
            
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        print("Invalid JSON received")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print("Error processing webhook:", str(e))
        raise HTTPException(status_code=500, detail=str(e))