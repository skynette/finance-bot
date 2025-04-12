from fastapi import HTTPException
import httpx
from api.schemas import TelegramUpdate, CommandResponse
from api.services.commnad_parser import CommandParser
from django.contrib.auth import get_user_model

User = get_user_model()

class TelegramService:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"

    async def process_update(self, update: TelegramUpdate) -> CommandResponse:
        if update.message:
            chat_id = update.message.chat.id
            text = update.message.text
            from_user = update.message.from_user

            await self.get_or_create_user_by_telegram_id(
                tg_id=from_user.id,
                first_name=from_user.first_name or "",
                username=from_user.username or ""
            )

            try:
                command_info = CommandParser.parse_command(text)
            except HTTPException as e:
                return CommandResponse(
                    status="error",
                    details={"detail": e.detail},
                    chat_id=chat_id
                )

            command = command_info.get("command")
            if command == "/add_income":
                return CommandResponse(
                    status="add_income_command",
                    details=command_info,
                    chat_id=chat_id
                )
            elif command == "/add_expense":
                return CommandResponse(
                    status="add_expense_command",
                    details=command_info,
                    chat_id=chat_id
                )
            elif command == "/help":
                return CommandResponse(
                    status="help_command",
                    details=command_info,
                    chat_id=chat_id
                )
            elif command == "/start":
                return CommandResponse(
                    status="start_command",
                    details={"welcome": True},
                    chat_id=chat_id
                )
            elif command == "/show_last":
                return CommandResponse(
                    status="show_last_command",
                    details={},
                    chat_id=chat_id
                )
            else:
                return CommandResponse(
                    status="unknown_command",
                    details={},
                    chat_id=chat_id
                )

        raise HTTPException(status_code=400, detail="Unsupported update")

    @staticmethod
    async def get_or_create_user_by_telegram_id(tg_id: int, first_name: str = "", username: str = ""):
        user, _ = await User.objects.aget_or_create(
            telegram_id=tg_id,
            defaults={"first_name": first_name, "username": username, "is_telegram_user": True}
        )
        return user

    async def _send_message(self, chat_id: int, text: str):
        print("✅ _Sending Message:", text)
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.api_url}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            )

    async def _send_message_with_keyboard(self, chat_id: int, text: str, buttons: list[list[str]]):
        keyboard = {
            "keyboard": [[{"text": btn} for btn in row] for row in buttons],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )
