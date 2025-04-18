from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api.schemas import CommandResponse
import logging

logger = logging.getLogger(__name__)

class MenuService:
    """Service for generating menu layouts and messages for the Telegram bot."""
    
    @staticmethod
    def get_main_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Generate the main menu with options for adding income/expense, viewing summary, and settings.
        
        Returns:
            tuple[str, InlineKeyboardMarkup]: The menu message and keyboard layout
        """
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Income", callback_data="menu_add_income"),
                InlineKeyboardButton("➖ Add Expense", callback_data="menu_add_expense"),
            ],
            [
                InlineKeyboardButton("📊 View Summary", callback_data="menu_summary"),
                InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="menu_help"),
            ],
        ]
        message = "Welcome to FinanceBot! What would you like to do?"
        return message, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_income_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Generate the income categories menu.
        
        Returns:
            tuple[str, InlineKeyboardMarkup]: The menu message and keyboard layout
        """
        keyboard = [
            [
                InlineKeyboardButton("💼 Salary", callback_data="income_salary"),
                InlineKeyboardButton("💰 Freelance", callback_data="income_freelance"),
            ],
            [
                InlineKeyboardButton("📈 Investment", callback_data="income_investment"),
                InlineKeyboardButton("🎁 Gift", callback_data="income_gift"),
            ],
            [
                InlineKeyboardButton("➕ Other", callback_data="income_other"),
            ],
            [
                InlineKeyboardButton("« Back to Main Menu", callback_data="back_to_main"),
            ],
        ]
        message = "Select income category:"
        return message, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_expense_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Generate the expense categories menu.
        
        Returns:
            tuple[str, InlineKeyboardMarkup]: The menu message and keyboard layout
        """
        keyboard = [
            [
                InlineKeyboardButton("🍔 Food", callback_data="expense_food"),
                InlineKeyboardButton("🏠 Rent", callback_data="expense_rent"),
            ],
            [
                InlineKeyboardButton("🚌 Transport", callback_data="expense_transport"),
                InlineKeyboardButton("🛍️ Shopping", callback_data="expense_shopping"),
            ],
            [
                InlineKeyboardButton("➕ Other", callback_data="expense_other"),
            ],
            [
                InlineKeyboardButton("« Back to Main Menu", callback_data="back_to_main"),
            ],
        ]
        message = "Select expense category:"
        return message, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_settings_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Generate the settings menu with options for currency and budget settings.
        
        Returns:
            tuple[str, InlineKeyboardMarkup]: The menu message and keyboard layout
        """
        keyboard = [
            [
                InlineKeyboardButton("💰 Set Currency", callback_data="settings_currency"),
                InlineKeyboardButton("📊 Set Budget", callback_data="settings_budget"),
            ],
            [
                InlineKeyboardButton("« Back to Main Menu", callback_data="back_to_main"),
            ],
        ]
        message = "Settings:"
        return message, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_help_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Generate the help menu with instructions on how to use the bot.
        
        Returns:
            tuple[str, InlineKeyboardMarkup]: The help message and keyboard layout
        """
        help_text = (
            "📚 *FinanceBot Help*\n\n"
            "Here's how to use the bot:\n\n"
            "1. *Add Income/Expense*\n"
            "   - Click ➕ Add Income or ➖ Add Expense\n"
            "   - Select a category\n"
            "   - Enter the amount\n"
            "   - Add a description (optional)\n\n"
            "2. *View Summary*\n"
            "   - Click 📊 View Summary to see your financial overview\n\n"
            "3. *Settings*\n"
            "   - Click ⚙️ Settings to configure your preferences\n\n"
            "Use the buttons below to navigate through the menus!"
        )
        
        keyboard = [
            [InlineKeyboardButton("« Back to Main Menu", callback_data="back_to_main")]
        ]
        return help_text, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_amount_input_message(category: str, transaction_type: str) -> tuple[str, InlineKeyboardMarkup]:
        """Generate the message for amount input.
        
        Args:
            category (str): The selected category
            transaction_type (str): Either 'income' or 'expense'
            
        Returns:
            tuple[str, InlineKeyboardMarkup]: The message and keyboard layout
        """
        keyboard = [
            [
                InlineKeyboardButton("« Back to Categories", callback_data=f"back_to_amount_{transaction_type}_{category}"),
            ],
        ]
        message = f"Enter the amount for {category} {transaction_type}:"
        return message, InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_description_input_message(category: str, amount: float, transaction_type: str) -> tuple[str, InlineKeyboardMarkup]:
        """Generate the message for description input.
        
        Args:
            category (str): The selected category
            amount (float): The entered amount
            transaction_type (str): Either 'income' or 'expense'
            
        Returns:
            tuple[str, InlineKeyboardMarkup]: The message and keyboard layout
        """
        message = f"Enter a description for {amount} {category} {transaction_type} (or skip):"
        
        # Format the amount to avoid any decimal point issues
        formatted_amount = str(amount).replace('.', '_')
        
        keyboard = [
            [InlineKeyboardButton("Skip Description", callback_data=f"skip_description_{transaction_type}_{formatted_amount}_{category}")],
            [InlineKeyboardButton("« Back to Amount", callback_data=f"back_to_amount_{transaction_type}_{category}")]
        ]
        return message, InlineKeyboardMarkup(keyboard) 