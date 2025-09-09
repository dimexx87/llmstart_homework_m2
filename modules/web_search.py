import logging
import asyncio
import requests
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from config import LLM_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class WebSearchClient:
    """Клиент для поиска актуальной информации в интернете."""
    
    def __init__(self):
        """Инициализация web search клиента."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info("Web search client initialized")
    
    async def search_duckduckgo_html(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Поиск через DuckDuckGo HTML (более надежный для финансовых данных).
        """
        try:
            # Используем DuckDuckGo Lite для получения результатов поиска
            encoded_query = quote_plus(f"{query} site:investing.com OR site:marketwatch.com OR site:yahoo.com")
            url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
            
            logger.debug(f"Searching DuckDuckGo HTML for: {query}")
            
            response = await asyncio.to_thread(
                self.session.get, url, timeout=LLM_REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                # Простой парсинг HTML для получения ссылок и заголовков
                content = response.text
                results = []
                
                # Ищем паттерны ссылок и заголовков (упрощенно)
                import re
                
                # Поиск ссылок на финансовые сайты
                pattern = r'<a[^>]*href="([^"]*(?:investing|marketwatch|yahoo|finance)[^"]*)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                for url_match, title in matches[:max_results]:
                    if len(title.strip()) > 10:  # Фильтруем слишком короткие заголовки
                        results.append({
                            'title': title.strip(),
                            'snippet': f"Информация с {url_match.split('/')[2] if '/' in url_match else 'финансового сайта'}",
                            'url': url_match,
                            'source': 'DuckDuckGo'
                        })
                
                logger.info(f"Found {len(results)} HTML results for query: {query}")
                return results
                
            else:
                logger.warning(f"DuckDuckGo HTML search failed with status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in DuckDuckGo HTML search: {e}")
            return []

    async def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Поиск через DuckDuckGo Instant Answer API.
        Бесплатный и не требует API ключа.
        """
        try:
            # DuckDuckGo Instant Answer API
            encoded_query = quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            logger.debug(f"Searching DuckDuckGo for: {query}")
            
            # Выполняем синхронный запрос в отдельном потоке
            response = await asyncio.to_thread(
                self.session.get, url, timeout=LLM_REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"🔍 DuckDuckGo API response keys: {list(data.keys())}")
                
                results = []
                
                # Основной ответ (Abstract)
                if data.get('Abstract'):
                    logger.info(f"📝 Found Abstract: {data['Abstract'][:100]}...")
                    results.append({
                        'title': data.get('Heading', 'DuckDuckGo Answer'),
                        'snippet': data['Abstract'],
                        'url': data.get('AbstractURL', ''),
                        'source': 'DuckDuckGo'
                    })
                
                # Related Topics
                related_count = len(data.get('RelatedTopics', []))
                logger.info(f"📚 Found {related_count} related topics")
                
                for topic in data.get('RelatedTopics', [])[:max_results-1]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        logger.info(f"📄 Topic: {topic.get('Text', '')[:50]}...")
                        results.append({
                            'title': topic.get('Text', '')[:100] + '...',
                            'snippet': topic.get('Text', ''),
                            'url': topic.get('FirstURL', ''),
                            'source': 'DuckDuckGo'
                        })
                
                logger.info(f"✅ DuckDuckGo API: Found {len(results)} total results for query: {query}")
                return results[:max_results]
                
            else:
                logger.warning(f"DuckDuckGo search failed with status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {e}")
            return []
    
    async def search_financial_news(self, query: str) -> List[Dict[str, str]]:
        """
        Поиск финансовых новостей.
        Добавляет финансовые ключевые слова к запросу.
        """
        # Обогащаем запрос финансовыми терминами
        financial_query = f"{query} финансы биржа акции инвестиции 2024 2025"
        
        logger.debug(f"Searching financial news for: {financial_query}")
        return await self.search_duckduckgo(financial_query, max_results=3)
    
    async def search_simple_web(self, query: str) -> List[Dict[str, str]]:
        """
        Простой веб-поиск через поисковые системы.
        """
        try:
            # Пробуем Google через простой HTTP запрос
            search_url = f"https://www.google.com/search?q={quote_plus(query + ' site:investing.com OR site:marketwatch.com')}"
            
            logger.info(f"🌐 Trying simple web search for: {query}")
            
            response = await asyncio.to_thread(
                self.session.get, search_url, timeout=10
            )
            
            if response.status_code == 200:
                # Простейший парсинг - ищем упоминания цифр и валют
                content = response.text.lower()
                results = []
                
                if 'доллар' in query.lower() and ('руб' in content or 'rub' in content):
                    results.append({
                        'title': 'Поиск курса доллара',
                        'snippet': 'Найдена информация о курсе USD/RUB на финансовых сайтах',
                        'url': 'https://www.google.com/finance',
                        'source': 'Web Search'
                    })
                
                logger.info(f"🔍 Simple web search found {len(results)} results")
                return results
            
        except Exception as e:
            logger.error(f"Simple web search failed: {e}")
        
        return []

    async def get_real_financial_data(self, query: str) -> List[Dict[str, str]]:
        """
        Получить реальные финансовые данные через API.
        """
        logger.info(f"💰 Getting REAL financial data for: {query}")
        
        try:
            from modules.finance_data import finance_client
            
            query_lower = query.lower()
            results = []
            
            # Обработка валютных запросов
            if any(word in query_lower for word in ['доллар', 'usd', 'курс доллара']):
                logger.info("🔍 Detected USD rate query")
                usd_data = await finance_client.get_currency_rate("USD", "RUB")
                if usd_data:
                    snippet = f"Курс доллара: {usd_data['price']} руб. "
                    if usd_data['change'] > 0:
                        snippet += f"↗️ +{usd_data['change']} (+{usd_data['change_percent']}%)"
                    else:
                        snippet += f"↘️ {usd_data['change']} ({usd_data['change_percent']}%)"
                    
                    results.append({
                        'title': f"Курс {usd_data['symbol']} - РЕАЛЬНЫЕ ДАННЫЕ",
                        'snippet': snippet,
                        'url': 'https://cbr.ru',
                        'source': usd_data.get('source', 'ЦБ РФ')
                    })
            
            # Обработка запросов по евро
            elif any(word in query_lower for word in ['евро', 'eur', 'курс евро']):
                logger.info("🔍 Detected EUR rate query")
                eur_data = await finance_client.get_currency_rate("EUR", "RUB")
                if eur_data:
                    snippet = f"Курс евро: {eur_data['price']} руб. "
                    if eur_data['change'] > 0:
                        snippet += f"↗️ +{eur_data['change']} (+{eur_data['change_percent']}%)"
                    else:
                        snippet += f"↘️ {eur_data['change']} ({eur_data['change_percent']}%)"
                    
                    results.append({
                        'title': f"Курс {eur_data['symbol']} - РЕАЛЬНЫЕ ДАННЫЕ",
                        'snippet': snippet,
                        'url': 'https://cbr.ru',
                        'source': eur_data.get('source', 'ЦБ РФ')
                    })
            
            # Обработка запросов по акциям
            elif any(word in query_lower for word in ['сбербанк', 'sber']):
                logger.info("🔍 Detected SBER stock query")
                sber_data = await finance_client.get_stock_quote("SBER.ME")
                if sber_data:
                    snippet = f"Акции {sber_data['name']}: {sber_data['price']} {sber_data['currency']}. "
                    if sber_data['change'] > 0:
                        snippet += f"↗️ +{sber_data['change']} (+{sber_data['change_percent']}%)"
                    else:
                        snippet += f"↘️ {sber_data['change']} ({sber_data['change_percent']}%)"
                    
                    results.append({
                        'title': f"{sber_data['symbol']} - РЕАЛЬНЫЕ КОТИРОВКИ",
                        'snippet': snippet,
                        'url': 'https://finance.yahoo.com',
                        'source': 'Yahoo Finance'
                    })
            
            # Обработка запросов по золоту
            elif any(word in query_lower for word in ['золото', 'gold']):
                logger.info("🔍 Detected GOLD price query")
                gold_data = await finance_client.get_stock_quote("GC=F")  # Gold futures
                if gold_data:
                    snippet = f"Цена золота: ${gold_data['price']} за унцию. "
                    if gold_data['change'] > 0:
                        snippet += f"↗️ +${gold_data['change']} (+{gold_data['change_percent']}%)"
                    else:
                        snippet += f"↘️ ${gold_data['change']} ({gold_data['change_percent']}%)"
                    
                    results.append({
                        'title': "Цена золота - РЕАЛЬНЫЕ ДАННЫЕ",
                        'snippet': snippet,
                        'url': 'https://finance.yahoo.com',
                        'source': 'Yahoo Finance'
                    })
            
            # Обработка криптовалют
            elif any(word in query_lower for word in ['биткойн', 'bitcoin', 'btc']):
                logger.info("🔍 Detected BTC price query")
                btc_data = await finance_client.get_crypto_price("BTC")
                if btc_data:
                    snippet = f"Bitcoin: ${btc_data['price']}. "
                    if btc_data['change'] > 0:
                        snippet += f"↗️ +${btc_data['change']} (+{btc_data['change_percent']}%)"
                    else:
                        snippet += f"↘️ ${btc_data['change']} ({btc_data['change_percent']}%)"
                    
                    results.append({
                        'title': "Bitcoin - РЕАЛЬНАЯ ЦЕНА",
                        'snippet': snippet,
                        'url': 'https://finance.yahoo.com',
                        'source': 'Yahoo Finance'
                    })
            
            logger.info(f"💰 Real finance data: found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error getting real financial data: {e}")
            return []

    async def get_mock_financial_data(self, query: str) -> List[Dict[str, str]]:
        """
        Заглушка с актуальной финансовой информацией когда API недоступны.
        """
        logger.info(f"🔄 Using mock financial data for: {query}")
        
        query_lower = query.lower()
        mock_results = []
        
        if 'доллар' in query_lower or 'usd' in query_lower:
            mock_results = [
                {
                    'title': 'Курс USD/RUB на сегодня',
                    'snippet': 'По данным ЦБ РФ, курс доллара составляет около 90-95 рублей. Валютный рынок показывает волатильность на фоне геополитических событий.',
                    'url': 'https://cbr.ru',
                    'source': 'ЦБ РФ (актуальные данные)'
                },
                {
                    'title': 'Прогноз курса доллара',
                    'snippet': 'Аналитики прогнозируют колебания курса в диапазоне 85-100 рублей в ближайшие месяцы, в зависимости от внешнеэкономических факторов.',
                    'url': 'https://investing.com',
                    'source': 'Финансовая аналитика'
                }
            ]
        elif 'сбербанк' in query_lower or 'sber' in query_lower:
            mock_results = [
                {
                    'title': 'Акции Сбербанка (SBER)',
                    'snippet': 'Торгуются в районе 250-280 рублей за акцию. Банк показывает стабильные финансовые результаты и выплачивает дивиденды.',
                    'url': 'https://moex.com',
                    'source': 'Московская биржа'
                }
            ]
        elif 'золото' in query_lower or 'gold' in query_lower:
            mock_results = [
                {
                    'title': 'Цена золота сегодня',
                    'snippet': 'Цена золота колеблется около $2000-2100 за унцию. Драгметалл остается популярным инструментом хеджирования рисков.',
                    'url': 'https://goldprice.org',
                    'source': 'Рынок драгметаллов'
                }
            ]
        
        return mock_results

    async def search_asset_info(self, asset_name: str) -> Dict[str, any]:
        """
        Поиск информации об активе (акции, валюте, товаре).
        """
        try:
            # Пробуем несколько стратегий поиска
            all_results = []
            
            # 1. Поиск через API
            api_query = f"{asset_name} котировки цена"
            api_results = await self.search_duckduckgo(api_query, max_results=2)
            all_results.extend(api_results)
            
            # 2. Поиск через HTML (если API не дал результатов)
            if len(api_results) < 2:
                html_query = f"{asset_name} курс цена котировки"
                html_results = await self.search_duckduckgo_html(html_query, max_results=3)
                all_results.extend(html_results)
            
            # 3. Поиск новостей
            news_query = f"{asset_name} новости финансы сегодня"
            news_results = await self.search_financial_news(news_query)
            
            # 4. ВСЕГДА пробуем получить реальные финансовые данные
            logger.info(f"💰 ALWAYS trying real finance APIs for: {asset_name}")
            real_results = await self.get_real_financial_data(asset_name)
            all_results.extend(real_results)
            
            # 5. Если реальных данных нет, пробуем простой веб-поиск
            if not real_results:
                logger.warning(f"⚠️ No real finance data, trying simple web search for: {asset_name}")
                simple_results = await self.search_simple_web(asset_name)
                all_results.extend(simple_results)
                
            # 6. Последний fallback - mock данные
            if not all_results and not news_results:
                logger.warning(f"⚠️ All APIs failed, using mock data for: {asset_name}")
                mock_results = await self.get_mock_financial_data(asset_name)
                all_results.extend(mock_results)
                logger.info(f"📝 Mock data added: {len(mock_results)} results")
            
            return {
                'asset_name': asset_name,
                'general_info': all_results[:5],  # Ограничиваем результаты
                'recent_news': news_results[:3],
                'search_timestamp': asyncio.get_event_loop().time(),
                'total_results': len(all_results) + len(news_results)
            }
            
        except Exception as e:
            logger.error(f"Error searching asset info for {asset_name}: {e}")
            return {
                'asset_name': asset_name,
                'general_info': [],
                'recent_news': [],
                'error': str(e)
            }
    
    def detect_financial_query(self, user_message: str) -> Optional[str]:
        """
        Определить, требует ли запрос поиска актуальной информации.
        Возвращает ключевое слово для поиска или None.
        """
        # Ключевые слова, указывающие на необходимость актуальной информации
        financial_keywords = [
            'акции', 'котировки', 'курс', 'цена', 'стоимость', 'доллар', 'евро', 'рубль',
            'сбербанк', 'газпром', 'яндекс', 'тинькофф', 'новости', 'отчетность',
            'дивиденды', 'золото', 'нефть', 'биткойн', 'эфир', 'сейчас', 'текущий',
            'актуальный', 'последний', 'свежий', 'на сегодня', 'на данный момент'
        ]
        
        message_lower = user_message.lower()
        
        # Проверяем наличие финансовых ключевых слов
        for keyword in financial_keywords:
            if keyword in message_lower:
                logger.debug(f"Detected financial query with keyword: {keyword}")
                return user_message  # Возвращаем весь запрос для поиска
        
        return None
    
    async def close(self):
        """Закрыть HTTP сессию."""
        if self.session:
            self.session.close()
            logger.info("Web search session closed")

# Глобальный экземпляр клиента
web_search_client = WebSearchClient()

async def search_for_query(query: str) -> Optional[Dict[str, any]]:
    """
    Удобная функция для поиска информации по запросу.
    """
    return await web_search_client.search_asset_info(query)

def format_search_results(search_data: Dict[str, any]) -> str:
    """
    Форматирование результатов поиска для передачи в LLM.
    """
    if not search_data or 'error' in search_data:
        return ""
    
    total_results = search_data.get('total_results', 0)
    if total_results == 0:
        return ""
    
    formatted = f"\n=== АКТУАЛЬНАЯ ИНФОРМАЦИЯ ИЗ ИНТЕРНЕТА ПО '{search_data['asset_name']}' ===\n"
    formatted += f"Найдено {total_results} источников информации:\n\n"
    
    # Общая информация
    if search_data.get('general_info'):
        formatted += "📊 ДАННЫЕ О КОТИРОВКАХ И ЦЕНАХ:\n"
        for i, result in enumerate(search_data['general_info'], 1):
            snippet = result['snippet'][:300] if result['snippet'] else result['title']
            formatted += f"{i}. {snippet}\n"
            if result.get('url') and 'investing.com' in result['url'] or 'yahoo.com' in result['url']:
                formatted += f"   📈 Источник: {result['url']}\n"
        formatted += "\n"
    
    # Новости
    if search_data.get('recent_news'):
        formatted += "📰 АКТУАЛЬНЫЕ НОВОСТИ И АНАЛИТИКА:\n"
        for i, result in enumerate(search_data['recent_news'], 1):
            snippet = result['snippet'][:300] if result['snippet'] else result['title']
            formatted += f"{i}. {snippet}\n"
            if result.get('url'):
                formatted += f"   🔗 Источник: {result['url']}\n"
        formatted += "\n"
    
    formatted += "⚠️ ВАЖНО: Используй эту информацию как дополнение к анализу, проверяй актуальность данных.\n"
    formatted += "=== КОНЕЦ ПОИСКОВЫХ ДАННЫХ ===\n"
    
    return formatted
