import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        "👋 Привет! Я LLM-ассистент компании.\n\n"
        "Я помогу вам:\n"
        "• Узнать о наших услугах\n"
        "• Ответить на вопросы\n"
        "• Подобрать подходящее решение\n\n"
        "Просто напишите ваш вопрос!"
    )
    
    await update.message.reply_text(welcome_message)

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo received text messages back to user."""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"User {user.id} ({user.username}) sent: {message_text[:50]}...")
    
    # Echo the message back
    response = f"Эхо: {message_text}"
    await update.message.reply_text(response)
    
    logger.info(f"Echoed message back to user {user.id}")

def setup_bot(token: str) -> Application:
    """Setup and configure the Telegram bot."""
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    
    # Add message handler for text messages (echo functionality)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    
    logger.info("Bot handlers configured")
    return application
