import logging
import asyncio
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
        "👋 Привет! Я ваш персональный финансовый аналитик.\n\n"
        "🎯 **Моя специализация:**\n"
        "• Анализ акций, облигаций, валют\n"
        "• Инвестиционные идеи и стратегии\n"
        "• Фундаментальный и технический анализ\n"
        "• Оценка рисков и возможностей\n\n"
        "💡 **Примеры вопросов:**\n"
        "• \"Проанализируй акции Сбербанка\"\n"
        "• \"Стоит ли покупать золото сейчас?\"\n"
        "• \"Какие ETF интересны для долгосрочных инвестиций?\"\n\n"
        "⚠️ *Помните: это не персональные инвестиционные советы*\n\n"
        "**Команды:**\n"
        "• /help - подробная справка\n"
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"Chat {chat_id}, User {user.id} ({user.username}) requested help")
    
    help_message = (
        "🏦 **Финансовый аналитик-бот**\n\n"
        "**Моя экспертиза:**\n"
        "📊 Фундаментальный и технический анализ\n"
        "📈 Фондовый рынок (акции, ETF, фонды)\n"
        "💱 Валютный рынок (USD, EUR, RUB и др.)\n"
        "🥇 Сырьевые товары (золото, нефть, газ)\n"
        "₿ Криптовалюты и DeFi\n"
        "🌍 Российский и зарубежные рынки\n\n"
        "**Формат анализа:**\n"
        "• Структурированный разбор активов\n"
        "• Плюсы и минусы инвестиций\n"
        "• Оценка рисков и возможностей\n"
        "• Учет разных временных горизонтов\n"
        "• 🌐 Поиск актуальной информации в интернете\n\n"
        "**Команды:**\n"
        "• `/start` - информация о боте\n"
        "• `/help` - эта справка\n"
        "• `/clear` - очистить историю\n\n"
        "**Технические ограничения:**\n"
        "• Максимум 4000 символов в сообщении\n"
        "• Сохраняю последние 20 сообщений\n"
        "• Таймаут ответа: 30 секунд\n\n"
        "⚠️ **Важно:** Это не персональные инвестиционные советы!\n"
        "Всегда проводите собственный анализ перед принятием решений."
    )
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages using LLM."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    logger.info(f"Chat {chat_id}, User {user.id} ({user.username}) sent: {message_text[:50]}...")
    
    try:
        # Показываем индикатор "печатает..."
        logger.info(f"🔄 Sending typing indicator to chat {chat_id}")
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        logger.info(f"✅ Typing indicator sent to chat {chat_id}")
        
        # Генерируем ответ через LLM с учетом истории чата
        # Создаем задачу для периодического обновления typing indicator
        async def keep_typing():
            while True:
                await asyncio.sleep(4)  # Обновляем каждые 4 секунды
                try:
                    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
                    logger.debug(f"🔄 Refreshed typing indicator for chat {chat_id}")
                except:
                    break
        
        typing_task = asyncio.create_task(keep_typing())
        
        try:
            response = await llm_client.generate_response(message_text, chat_id)
        finally:
            typing_task.cancel()  # Останавливаем typing indicator
        
        # Пытаемся отправить ответ с retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await update.message.reply_text(response)
                logger.info(f"LLM response sent to chat {chat_id} (attempt {attempt + 1})")
                break
            except Exception as send_error:
                logger.warning(f"Failed to send response attempt {attempt + 1}: {send_error}")
                if attempt == max_retries - 1:
                    # Последняя попытка с упрощенным сообщением
                    await update.message.reply_text("Ответ получен, но возникли проблемы с отправкой. Попробуйте повторить запрос.")
                else:
                    await asyncio.sleep(1)  # Пауза перед retry
        
    except Exception as e:
        logger.error(f"Error processing message for chat {chat_id}: {e}")
        try:
            error_message = "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
            await update.message.reply_text(error_message)
        except:
            logger.error(f"Failed to send error message to chat {chat_id}")

def setup_bot(token: str) -> Application:
    """Setup and configure the Telegram bot."""
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Add message handler for text messages (LLM functionality)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("Bot handlers configured")
    return application
