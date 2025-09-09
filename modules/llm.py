import logging
import openai
import asyncio
from typing import List, Dict, Any, Optional
from config import OPENROUTER_API_KEY, MAX_MESSAGE_LENGTH, MAX_HISTORY_MESSAGES, LLM_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

try:
    from modules.web_search import web_search_client, format_search_results
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Web search not available: {e}")
    WEB_SEARCH_AVAILABLE = False
    web_search_client = None
    format_search_results = None

# Системный промпт как константа
SYSTEM_PROMPT = """Ты - опытный финансовый аналитик и консультант по инвестициям с глубокими знаниями фондового и валютного рынков.

ТВОЯ ЭКСПЕРТИЗА:
• Фундаментальный и технический анализ
• Макроэкономика и геополитика
• Акции, облигации, валюты, сырьевые товары
• ETF, фонды, деривативы
• Криптовалюты и DeFi
• Российский и международные рынки

СТИЛЬ АНАЛИЗА:
• Структурированный подход: тезис → аргументы → выводы
• Обязательно указывай риски и ограничения
• Приводи конкретные цифры и метрики когда возможно
• Учитывай разные временные горизонты (краткосрочный/долгосрочный)
• Рассматривай различные сценарии развития

ФОРМАТ ОТВЕТОВ (КРАТКИЙ):
📊 **Анализ:** текущая ситуация в 1-2 предложения
📈 **Плюсы:** 2-3 ключевых аргумента за
📉 **Минусы:** 2-3 главных риска  
💡 **Рекомендация:** четкий вывод
⚠️ **Важно:** обязательные дисклеймеры

СТИЛЬ: лаконичный, без воды, максимум конкретики

ПРИНЦИПЫ:
• Честность: признавайся в неопределенности рынков
• Баланс: показывай как возможности, так и угрозы
• Образование: объясняй логику рассуждений
• Ответственность: подчеркивай важность собственного анализа
• Актуальность: учитывай текущую рыночную ситуацию
• КРАТКОСТЬ: ответ должен быть лаконичным, максимум 200-300 слов

ВАЖНЫЕ ДИСКЛЕЙМЕРЫ:
- Это не персональная инвестиционная рекомендация
- Всегда делай собственный анализ перед инвестированием
- Прошлая доходность не гарантирует будущих результатов
- Инвестиции связаны с риском потери капитала

Отвечай на русском языке профессионально, но доступно.

КРИТИЧЕСКИ ВАЖНО: Твой ответ должен быть КРАТКИМ и СТРУКТУРИРОВАННЫМ:
- Общая длина: не более 200-300 слов
- Используй ТОЛЬКО указанный формат с эмодзи
- Без лишних деталей и повторений
- Максимум конкретики, минимум текста"""

# Глобальное хранилище истории диалогов: chat_id -> list сообщений
chat_histories: Dict[int, List[Dict[str, str]]] = {}

def add_to_history(chat_id: int, role: str, content: str) -> None:
    """Добавить сообщение в историю чата."""
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    chat_histories[chat_id].append({"role": role, "content": content})
    
    # Ограничиваем историю последними N сообщениями (исключая системный промпт)
    if len(chat_histories[chat_id]) > MAX_HISTORY_MESSAGES:
        chat_histories[chat_id] = chat_histories[chat_id][-MAX_HISTORY_MESSAGES:]
    
    logger.debug(f"Added {role} message to chat {chat_id} history, total messages: {len(chat_histories[chat_id])}")

def get_chat_context(chat_id: int) -> List[Dict[str, str]]:
    """Получить контекст чата для LLM (системный промпт + история)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if chat_id in chat_histories:
        messages.extend(chat_histories[chat_id])
    
    return messages

def clear_chat_history(chat_id: int) -> None:
    """Очистить историю чата."""
    if chat_id in chat_histories:
        del chat_histories[chat_id]
        logger.info(f"Chat history cleared for chat {chat_id}")

class LLMClient:
    """Клиент для работы с OpenRouter API через OpenAI SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Инициализация клиента OpenRouter."""
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
            
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        logger.info("LLM client initialized")
    
    async def generate_response(self, user_message: str, chat_id: int) -> str:
        """Генерация ответа через LLM с учетом истории чата."""
        # Валидация длины сообщения
        if len(user_message) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long from chat {chat_id}: {len(user_message)} chars")
            return f"Сообщение слишком длинное ({len(user_message)} символов). Максимум {MAX_MESSAGE_LENGTH} символов."
        
        # Проверка на пустое сообщение
        if not user_message.strip():
            return "Пожалуйста, напишите ваш вопрос."
            
        try:
            logger.debug(f"LLM request from chat {chat_id}: {user_message[:100]}...")
            
            # Проверяем, нужна ли актуальная информация (только если web search доступен)
            current_info = ""
            
            if WEB_SEARCH_AVAILABLE and web_search_client:
                search_query = web_search_client.detect_financial_query(user_message)
                if search_query:
                    logger.info(f"🔍 DETECTED FINANCIAL QUERY: {search_query}")
                    try:
                        search_results = await web_search_client.search_asset_info(search_query)
                        logger.info(f"📊 SEARCH RESULTS: {search_results}")
                        current_info = format_search_results(search_results)
                        logger.info(f"📝 FORMATTED INFO LENGTH: {len(current_info)} chars")
                        if current_info:
                            logger.info(f"📋 FORMATTED CONTENT: {current_info[:500]}...")
                        else:
                            logger.warning("⚠️ NO SEARCH RESULTS TO FORMAT")
                    except Exception as search_error:
                        logger.error(f"❌ SEARCH ERROR: {search_error}")
                        current_info = ""
                else:
                    logger.info(f"❌ NO FINANCIAL KEYWORDS DETECTED in: {user_message}")
            else:
                logger.warning("⚠️ WEB SEARCH NOT AVAILABLE, using LLM knowledge only")
            
            # Добавляем сообщение пользователя в историю
            add_to_history(chat_id, "user", user_message)
            
            # Получаем контекст чата (системный промпт + история)
            messages = get_chat_context(chat_id)
            
            # Если есть актуальная информация, добавляем её в контекст
            if current_info:
                logger.info("🔗 ADDING SEARCH INFO TO LLM CONTEXT")
                # Добавляем актуальную информацию как системное сообщение
                messages.append({
                    "role": "system", 
                    "content": f"АКТУАЛЬНАЯ ИНФОРМАЦИЯ ИЗ ИНТЕРНЕТА:\n{current_info}\n\nИспользуй эту информацию в своем анализе, но не копируй дословно. Интегрируй данные в свой экспертный анализ."
                })
            else:
                logger.info("📝 NO SEARCH INFO TO ADD, using LLM knowledge only")
            
            logger.info(f"🚀 SENDING REQUEST TO LLM with {len(messages)} messages")
            
            # Отправляем запрос к OpenRouter с таймаутом
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="anthropic/claude-sonnet-4",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                ),
                timeout=LLM_REQUEST_TIMEOUT
            )
            
            logger.info("✅ LLM RESPONSE RECEIVED")
            
            # Извлекаем ответ
            llm_response = response.choices[0].message.content
            
            if not llm_response:
                logger.warning(f"Empty response from LLM for chat {chat_id}")
                return "Получен пустой ответ от ассистента. Попробуйте переформулировать вопрос."
            
            # Добавляем ответ ассистента в историю
            add_to_history(chat_id, "assistant", llm_response)
            
            logger.debug(f"LLM response to chat {chat_id}: {llm_response[:100]}...")
            logger.info(f"LLM request completed successfully for chat {chat_id}")
            
            return llm_response
            
        except asyncio.TimeoutError:
            logger.error(f"LLM request timeout for chat {chat_id}")
            return "Запрос занял слишком много времени. Попробуйте позже или упростите вопрос."
            
        except openai.RateLimitError:
            logger.error(f"Rate limit exceeded for chat {chat_id}")
            return "Превышен лимит запросов. Пожалуйста, подождите немного перед следующим сообщением."
            
        except openai.AuthenticationError:
            logger.error(f"Authentication error for chat {chat_id}")
            return "Ошибка аутентификации. Обратитесь к администратору."
            
        except openai.APIConnectionError:
            logger.error(f"API connection error for chat {chat_id}")
            return "Проблемы с подключением к сервису. Попробуйте позже."
            
        except Exception as e:
            logger.error(f"Unexpected error for chat {chat_id}: {e}")
            return "Произошла неожиданная ошибка. Попробуйте позже или обратитесь к поддержке."

# Глобальный экземпляр клиента
llm_client = LLMClient()
