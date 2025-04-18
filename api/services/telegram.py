from fastapi import HTTPException
from api.schemas import TelegramUpdate, CommandResponse
from api.services.commnad_parser import CommandParser
from api.services.menu import MenuService
from api.services.finance import FinanceService
from django.contrib.auth import get_user_model
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

User = get_user_model()

class TelegramService:
    """Service for handling Telegram bot interactions and state management."""
    
    def __init__(self, token: str):
        """Initialize the Telegram service with a bot token.
        
        Args:
            token (str): The Telegram bot token
        """
        self.token = token
        self.bot = Bot(token=token)
        self.application = None
        self.user_states = {}  # Store user states for multi-step interactions

    async def initialize(self):
        """Initialize the bot and application with all necessary handlers."""
        self.application = Application.builder().bot(self.bot).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        await self.application.initialize()
        logger.info("TelegramService initialized successfully")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command by showing the main menu."""
        # Clear any existing state for this user
        user_id = update.effective_user.id
        if user_id in self.user_states:
            del self.user_states[user_id]
            
        message, keyboard = MenuService.get_main_menu()
        await update.message.reply_text(message, reply_markup=keyboard)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command by showing the help menu."""
        message, keyboard = MenuService.get_help_menu()
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages for amount and description input.
        
        This method processes user input for:
        - Amount input when adding income/expense
        - Description input when adding income/expense
        """
        user_id = update.effective_user.id
        text = update.message.text
        
        # Check if user is in a state
        if user_id in self.user_states:
            state = self.user_states[user_id]
            
            if state["type"] == "amount":
                try:
                    amount = float(text)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    
                    # Update state with amount
                    state["amount"] = amount
                    state["type"] = "description"
                    
                    # Show description input message
                    message, keyboard = MenuService.get_description_input_message(
                        state["category"],
                        amount,
                        state["transaction_type"]
                    )
                    await update.message.reply_text(message, reply_markup=keyboard)
                    
                except ValueError:
                    await update.message.reply_text("Please enter a valid positive number for the amount.")
                    
            elif state["type"] == "description":
                # Create the record
                record_data = {
                    "amount": state["amount"],
                    "category_name": state["category"],
                    "description": text
                }
                
                user = await User.objects.aget(telegram_id=user_id)
                
                if state["transaction_type"] == "income":
                    response = await FinanceService.create_income(record_data, user.id)
                else:
                    response = await FinanceService.create_expense(record_data, user.id)
                
                # Clear user state before showing the message
                del self.user_states[user_id]
                
                # Show success message and main menu
                if response.status == "success":
                    message, keyboard = MenuService.get_main_menu()
                    await update.message.reply_text(
                        f"✅ {state['transaction_type'].capitalize()} of {state['amount']} for {state['category']} has been recorded!",
                        reply_markup=keyboard
                    )
                else:
                    message, keyboard = MenuService.get_main_menu()
                    await update.message.reply_text(
                        f"❌ Failed to record {state['transaction_type']}: {response.details.get('detail', 'Unknown error')}",
                        reply_markup=keyboard
                    )
        else:
            # If user is not in a state but sends a message, it might be an old transaction
            await update.message.reply_text(
                "❌ This action is no longer valid. Please use the menu to start a new transaction.",
                reply_markup=MenuService.get_main_menu()[1]
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button presses and update the menu accordingly.
        
        This method processes all button interactions in the bot, including:
        - Navigation between menus
        - Income/expense category selection
        - Amount and description input
        - Feature access (coming soon features)
        """
        try:
            query = update.callback_query
            await query.answer()
            
            button_data = query.data
            user_id = query.from_user.id
            
            # Clear state when starting a new transaction
            if button_data in ["menu_add_income", "menu_add_expense"]:
                if user_id in self.user_states:
                    del self.user_states[user_id]

            # Check if this is a state-dependent button and validate state
            if (button_data.startswith("skip_description_") or 
                button_data.startswith("back_to_amount_")):
                if user_id not in self.user_states:
                    await query.edit_message_text(
                        "❌ This action is no longer valid. Please use the menu to start a new transaction.",
                        reply_markup=MenuService.get_main_menu()[1]
                    )
                    return

            if button_data == "back_to_main":
                # Clear state when going back to main menu
                if user_id in self.user_states:
                    del self.user_states[user_id]
                    
                message, keyboard = MenuService.get_main_menu()
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data == "menu_add_income":
                message, keyboard = MenuService.get_income_menu()
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data == "menu_add_expense":
                message, keyboard = MenuService.get_expense_menu()
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data == "menu_settings":
                message, keyboard = MenuService.get_settings_menu()
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data == "menu_help":
                message, keyboard = MenuService.get_help_menu()
                await query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")

            elif button_data == "menu_summary":
                # Coming soon message for summary feature
                message, keyboard = MenuService.get_main_menu()
                await query.edit_message_text(
                    "📊 Summary feature coming soon!\n\nUse the menu below to add income or expenses.",
                    reply_markup=keyboard
                )

            elif button_data == "settings_currency":
                # Coming soon message for currency settings
                message, keyboard = MenuService.get_settings_menu()
                await query.edit_message_text(
                    "💰 Currency settings coming soon!\n\nYou can still add income and expenses in your current currency.",
                    reply_markup=keyboard
                )

            elif button_data == "settings_budget":
                # Coming soon message for budget settings
                message, keyboard = MenuService.get_settings_menu()
                await query.edit_message_text(
                    "📊 Budget settings coming soon!\n\nYou can still track your income and expenses.",
                    reply_markup=keyboard
                )

            elif button_data.startswith("income_") or button_data.startswith("expense_"):
                # Handle income/expense category selection
                type = "income" if button_data.startswith("income_") else "expense"
                category = button_data.split("_", 1)[1]
                
                # Store user state
                self.user_states[user_id] = {
                    "type": "amount",
                    "transaction_type": type,
                    "category": category
                }
                
                message, keyboard = MenuService.get_amount_input_message(category, type)
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data.startswith("back_to_amount_"):
                # Handle going back to amount input
                parts = button_data.split("_", 3)
                if len(parts) != 4:
                    await query.edit_message_text("❌ Invalid button data. Please try again.")
                    return
                    
                type = parts[2]
                category = parts[3]
                
                # Update user state
                self.user_states[user_id] = {
                    "type": "amount",
                    "transaction_type": type,
                    "category": category
                }
                
                message, keyboard = MenuService.get_amount_input_message(category, type)
                await query.edit_message_text(message, reply_markup=keyboard)

            elif button_data.startswith("skip_description_"):
                # Handle skipping description
                parts = button_data.split("_")
                if len(parts) < 5:
                    await query.edit_message_text("❌ Invalid button data. Please try again.")
                    return
                    
                type = parts[2]
                amount_str = parts[3] + "." + parts[4]  # Combine the amount parts
                amount = float(amount_str)
                category = parts[5]  # Category is now the 6th part
                
                # Create record without description
                record_data = {
                    "amount": amount,
                    "category_name": category,
                    "description": ""
                }
                
                user = await User.objects.aget(telegram_id=user_id)
                
                if type == "income":
                    response = await FinanceService.create_income(record_data, user.id)
                else:
                    response = await FinanceService.create_expense(record_data, user.id)
                
                # Clear user state before showing the message
                del self.user_states[user_id]
                
                # Show success message and main menu
                if response.status == "success":
                    message, keyboard = MenuService.get_main_menu()
                    await query.edit_message_text(
                        f"✅ {type.capitalize()} of {amount} for {category} has been recorded!",
                        reply_markup=keyboard
                    )
                else:
                    message, keyboard = MenuService.get_main_menu()
                    await query.edit_message_text(
                        f"❌ Failed to record {type}: {response.details.get('detail', 'Unknown error')}",
                        reply_markup=keyboard
                    )
            
            else:
                # This is for truly unknown commands that are not part of our bot's scope
                message, keyboard = MenuService.get_main_menu()
                await query.edit_message_text(
                    "❌ Unknown command. Here's what you can do:",
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"Error in button_callback: {str(e)}", exc_info=True)
            await query.edit_message_text("❌ An error occurred. Please try again.")

    async def process_update(self, update: TelegramUpdate) -> CommandResponse:
        """Process incoming Telegram updates.
        
        This method converts the incoming update to the format expected by python-telegram-bot
        and processes it through the application.
        
        Args:
            update (TelegramUpdate): The incoming update from Telegram
            
        Returns:
            CommandResponse: The response indicating the status of the update processing
        """
        try:
            # Convert the update to a format that python-telegram-bot can handle
            update_dict = update.model_dump()
            
            # Ensure the update has the correct structure for python-telegram-bot
            if update.callback_query:
                # Convert our CallbackQuery to the format expected by python-telegram-bot
                callback_query = update.callback_query.model_dump()
                callback_query["from"] = callback_query.pop("from_user")
                update_dict["callback_query"] = callback_query
            elif update.message:
                # Convert our Message to the format expected by python-telegram-bot
                message = update.message.model_dump()
                message["from"] = message.pop("from_user")
                update_dict["message"] = message
            
            telegram_update = Update.de_json(update_dict, self.bot)
            
            # Process the update through the application
            await self.application.process_update(telegram_update)
            
            # Get chat_id from either message or callback_query
            chat_id = None
            if update.message:
                chat_id = update.message.chat.id
            elif update.callback_query and update.callback_query.message:
                chat_id = update.callback_query.message.chat.id
            
            return CommandResponse(
                status="success",
                details={"message": "Update processed successfully"},
                chat_id=chat_id
            )

        except Exception as e:
            logger.error(f"Error processing update: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_or_create_user_by_telegram_id(tg_id: int, first_name: str = "", username: str = ""):
        """Get or create a user based on their Telegram ID.
        
        Args:
            tg_id (int): The Telegram user ID
            first_name (str, optional): The user's first name
            username (str, optional): The user's username
            
        Returns:
            User: The user object
        """
        user, _ = await User.objects.aget_or_create(
            telegram_id=tg_id,
            defaults={"first_name": first_name, "username": username, "is_telegram_user": True}
        )
        return user
