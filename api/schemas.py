from pydantic import BaseModel, Field
from typing import Optional, List

class MessageEntity(BaseModel):
    offset: int
    length: int
    type: str

class TelegramUser(BaseModel):
    id: int
    is_bot: bool = False
    first_name: str
    username: Optional[str] = None
    language_code: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    type: str
    first_name: Optional[str] = None
    username: Optional[str] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_user: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None

class CallbackQuery(BaseModel):
    id: str
    from_user: TelegramUser = Field(alias="from")
    message: Optional[TelegramMessage] = None
    inline_message_id: Optional[str] = None
    chat_instance: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None

class FinancialRecord(BaseModel):
    amount: float
    currency_code: str
    category_name: str
    description: Optional[str] = None

class CommandResponse(BaseModel):
    status: str
    details: dict
    chat_id: Optional[int] = None  