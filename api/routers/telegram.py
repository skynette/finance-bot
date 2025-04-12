import os
from fastapi import APIRouter, Request
from api.schemas import TelegramUpdate
from api.services.telegram import TelegramService
from api.services.finance import FinanceService
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

load_dotenv()
User = get_user_model()

router = APIRouter()
token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_service = TelegramService(token=token)

help_text = (
"""*FinanceBot Help:*\n
Use the following commands:
`/add_income [amount] [category] [description]` - Log an income
`/add_expense [amount] [category] [description]` - Log an expense
`/help` - Show this message again"""
)
    
@router.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = TelegramUpdate(**update_data)
    result = await telegram_service.process_update(update)
        
    if result.status == "start_command":
        await telegram_service._send_message(
            result.chat_id,
            "Welcome to FinanceBot! Use /help to see available commands."
        )
        return {"status": "start_command handled"}
    
    if result.status == "error":
        await telegram_service._send_message(result.chat_id, help_text)
        return {"status": "error_handled"}
    
    elif result.status == "help_command":
        await telegram_service._send_message(result.chat_id, help_text)
        return {"status": "help_command handled"}

    elif result.status == "add_income_command":
        response = await FinanceService.handle_add_income_command(result.details['args'], update.message.from_user.id)
        if response.status == "error":
            await telegram_service._send_message(
                result.chat_id,
                response.details.get("message", "Something went wrong.")
            )
        elif response.status == "success":
            await telegram_service._send_message(
                result.chat_id,
                response.details.get("message", "Success do not worry.")
            )
        
        return {"status": "add_income_command handled"}

    elif result.status == "add_expense_command":
        response = await FinanceService.handle_add_expense_command(
            result.details['args'],
            update.message.from_user.id
        )
        
        if response.status == "error":
            print("❌Error response", response)
            await telegram_service._send_message(
                result.chat_id,
                response.details.get("message", "Something went wrong.")
            )
        
        elif response.status == "success":
            print("👍Success response", response)
            await telegram_service._send_message(
                result.chat_id,
                response.details.get("message", "Success do not worry.")
            )
        return {"status": "add_expense_command handled"}
    else:
        print("😒 ELSE CASE HANDLED")
        await telegram_service._send_message(
            update.message.chat.id,
            "ERROR UNKNOWN COMMAND"
        )
    return {"status": "ok"}

@router.get("/")
async def home(request: Request):
    return {"OK": "Alive"}