import os, httpx
from api.schemas import TelegramUpdate, CommandResponse
from utils.parsers import parse_income_command, parse_expense_command
from typing import Optional
from fastapi import HTTPException

from dotenv import load_dotenv
load_dotenv()

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("Telegram bot token is not set in environment variables.")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def _send_message(self, chat_id: int, text: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
            )
            response.raise_for_status()
            return response.json()
 
    @staticmethod
    async def process_update(update_data: dict) -> CommandResponse:
        try:
            # Parse the incoming update
            update = TelegramUpdate(**update_data)
            
            # Get chat_id from wherever possible in the update
            chat_id = None
            if update.message:
                chat_id = update.message.chat.id
            elif update.edited_message:
                chat_id = update.edited_message.chat.id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat.id
            
            # If we can't determine a chat to reply to
            if not chat_id:
                return CommandResponse(
                    status="error",
                    details={"detail": "No chat available for reply"},
                    chat_id=None
                )

            # Process messages
            if update.message:
                if command_info := TelegramService.extract_command(update.message):
                    command_info["chat_id"] = chat_id
                    return await TelegramService.process_command(command_info)
                
                return CommandResponse(
                    status="message_received",
                    details={"text": update.message.text},
                    chat_id=chat_id
                )

            # If we get here, it's an update type we don't handle
            return CommandResponse(
                status="ignored",
                details={"reason": "Unhandled update type"},
                chat_id=chat_id
            )

        except Exception as e:
            print(f"Error processing update: {str(e)}")
            return CommandResponse(
                status="error",
                details={"detail": str(e)},
                chat_id=chat_id if 'chat_id' in locals() else None
            )
    
    @staticmethod
    def extract_command(message) -> Optional[dict]:
        if not message.text or not message.entities:
            return None
            
        for entity in message.entities:
            if entity.type == "bot_command":
                command = message.text[entity.offset:entity.offset+entity.length]
                args = message.text[entity.offset+entity.length:].strip()
                return {
                    "command": command.lower(),
                    "args": args.split() if args else []
                }
        return None
    
    @staticmethod
    async def process_command(command_info: dict) -> CommandResponse:
        try:
            command = command_info["command"]
            
            if command == "/help":
                return CommandResponse(
                    status="help_command",
                    details={},
                    chat_id=command_info.get("chat_id")
                )
            elif command == "/add_income":
                record = parse_income_command(command_info["args"])
                return CommandResponse(
                    status="income_command",
                    details={"record": record.dict()},
                    chat_id=command_info.get("chat_id")
                )
            elif command == "/add_expense":
                record = parse_expense_command(command_info["args"])
                return CommandResponse(
                    status="expense_command",
                    details={"record": record.dict()},
                    chat_id=command_info.get("chat_id")
                )
            else:
                return CommandResponse(
                    status="unrecognized_command",
                    details={"command": command},
                    chat_id=command_info.get("chat_id")
                )
        except HTTPException as e:
            return CommandResponse(
                status="error",
                details={"detail": e.detail},
                chat_id=command_info.get("chat_id")
            )
