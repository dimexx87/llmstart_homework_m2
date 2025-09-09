import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from modules.llm import llm_client, clear_chat_history

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"Chat {chat_id}, User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        "👋 Привет! Я LLM-ассистент компании.\n\n"
        "Я помогу вам:\n"
        "• Узнать о наших услугах\n"
        "• Ответить на вопросы\n"
        "• Подобрать подходящее решение\n\n"
        "Просто напишите ваш вопрос!\n\n"
        "Доступные команды:\n"
        "• /clear - очистить историю диалога"
    )
    
    await update.message.reply_text(welcome_message)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command to clear chat history."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    clear_chat_history(chat_id)
    logger.info(f"Chat {chat_id}, User {user.id} ({user.username}) cleared chat history")
    
    await update.message.reply_text("🗑️ История диалога очищена. Начинаем с чистого листа!")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages using LLM."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    logger.info(f"Chat {chat_id}, User {user.id} ({user.username}) sent: {message_text[:50]}...")
    
    try:
        # Генерируем ответ через LLM с учетом истории чата
        response = await llm_client.generate_response(message_text, chat_id)
        await update.message.reply_text(response)
        
        logger.info(f"LLM response sent to chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error processing message for chat {chat_id}: {e}")
        error_message = "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
        await update.message.reply_text(error_message)

def setup_bot(token: str) -> Application:
    """Setup and configure the Telegram bot."""
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Add message handler for text messages (LLM functionality)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("Bot handlers configured")
    return application
