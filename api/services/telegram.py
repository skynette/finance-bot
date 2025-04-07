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
        print("Telegram bot token:", self.bot_token)
        if not self.bot_token:
            raise ValueError("Telegram bot token is not set in environment variables.")
        print("Initializing TelegramService with bot token:", self.bot_token)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def _send_message(self, chat_id: int, text: str):
        print("Sending message to chat_id by calling API:", chat_id, "with text:", text)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
            )
            print("Response from Telegram API:", response.status_code, response.text)
            response.raise_for_status()
            return response.json()
 
    @staticmethod
    async def process_update(update_data: dict) -> CommandResponse:
        try:
            update = TelegramUpdate(**update_data)
            if not update.message:
                return CommandResponse(
                    status="ignored", 
                    details={"reason": "No message"},
                    chat_id=None
                )
                
            if command_info := TelegramService.extract_command(update.message):
                return await TelegramService.process_command(command_info)
            
            return CommandResponse(
                status="message_received",
                details={"text": update.message.text},
                chat_id=update.message.chat.id
            )
        except Exception as e:
            return CommandResponse(
                status="error",
                details={"detail": str(e)},
                chat_id=update.message.chat.id if update and update.message else None
            )
    
    @staticmethod
    def extract_command(message) -> Optional[dict]:
        print("Extracting command from message:", message)
        if not message.text or not message.entities:
            print("No text or entities in message")
            return None
            
        for entity in message.entities:
            if entity.type == "bot_command":
                command = message.text[entity.offset:entity.offset+entity.length]
                args = message.text[entity.offset+entity.length:].strip()
                print("Command found:", command, "with args:", args)
                return {
                    "command": command.lower(),
                    "args": args.split() if args else []
                }
        print("No command found in message")
        return None
    
    @staticmethod
    async def process_command(command_info: dict) -> CommandResponse:
        print("Processing command:", command_info)
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
                    details={"record": record.dict()}
                )
            elif command == "/add_expense":
                record = parse_expense_command(command_info["args"])
                return CommandResponse(
                    status="expense_command",
                    details={"record": record.dict()}
                )
            else:
                return CommandResponse(
                    status="unrecognized_command",
                    details={"command": command}
                )
        except HTTPException as e:
            return CommandResponse(
                status="error",
                details={"detail": e.detail}
            )
