import os
import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter, Request, FastAPI, HTTPException
from api.schemas import TelegramUpdate
from api.services.telegram import TelegramService
from api.services.finance import FinanceService
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
User = get_user_model()

router = APIRouter()
token = os.environ.get("TELEGRAM_BOT_TOKEN")
webhook_url = os.environ.get("WEBHOOK_URL")
telegram_service = TelegramService(token=token)

help_text = (
"""*FinanceBot Help:*\n
Use the following commands:
`/add_income [amount] [category] [description]` - Log an income
`/add_expense [amount] [category] [description]` - Log an expense
`/help` - Show this message again"""
)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Initialize the bot
    await telegram_service.initialize()
    
    # Set webhook
    webhook_info = await telegram_service.bot.get_webhook_info()
    
    # Only set webhook if it's not already set correctly
    if webhook_info.url != webhook_url:
        await telegram_service.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Webhook already set correctly")
    
    logger.info("Bot and application initialized successfully")
    
    yield  # This is where the app runs
    
    # Shutdown: Remove webhook and shutdown application
    if telegram_service.bot and telegram_service.bot._initialized:
        await telegram_service.bot.delete_webhook()
        await telegram_service.bot.shutdown()
        logger.info("Bot shut down")
    
    if telegram_service.application and telegram_service.application._initialized:
        await telegram_service.application.shutdown()
        logger.info("Application shut down")

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Process incoming Telegram updates and execute bot commands.
    
    This endpoint receives updates from Telegram's webhook system and processes them
    according to the bot's menu structure. It supports various commands for managing
    financial transactions through an interactive menu system.
    """
    try:
        update_data = await request.json()
        logger.info(f"Received webhook update: {update_data}")
        
        # Validate update data
        if not update_data:
            logger.error("Empty update data received")
            raise HTTPException(status_code=400, detail="Empty update data")
            
        # Create TelegramUpdate object
        try:
            update = TelegramUpdate(**update_data)
        except Exception as e:
            logger.error(f"Error parsing update data: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid update format: {str(e)}")
        
        # Process the update through the Telegram service
        try:
            result = await telegram_service.process_update(update)
            logger.info(f"Update processed successfully: {result}")
            return {"status": "success", "details": result.details}
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing update: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def home(request: Request):
    """Health check endpoint."""
    return {"OK": "Alive"}