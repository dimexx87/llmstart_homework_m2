"""
Модуль для работы с финансовыми API.
"""
import logging
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import requests

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

logger = logging.getLogger(__name__)

class FinanceDataClient:
    """
    Клиент для получения финансовых данных через API.
    
    ДОСТУПНЫЕ ИНТЕГРАЦИИ:
    - Yahoo Finance API - реальные котировки ✅
    - ЦБ РФ API - курсы валют ✅
    - CoinGecko - криптовалютные данные (планируется)
    """
    
    def __init__(self):
        self.supported_apis = {
            'yahoo_finance': YFINANCE_AVAILABLE,
            'cbr_ru': True,           # ЦБ РФ не требует библиотек
            'coinGecko': False,       # TODO: реализовать
        }
        logger.info(f"🏦 Finance data client initialized. Available APIs: {[k for k, v in self.supported_apis.items() if v]}")
        if not YFINANCE_AVAILABLE:
            logger.error("❌ yfinance NOT INSTALLED! Run: pip install yfinance")
        else:
            logger.info("✅ yfinance available for real data")
    
    async def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Получить текущую котировку акции через Yahoo Finance.
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available")
            return None
            
        try:
            logger.info(f"🔍 Getting stock quote for {symbol}")
            
            # Выполняем запрос в отдельном потоке
            ticker_data = await asyncio.to_thread(self._fetch_stock_data, symbol)
            
            if ticker_data:
                logger.info(f"✅ Stock data found for {symbol}: {ticker_data['price']}")
                return ticker_data
            else:
                logger.warning(f"❌ No stock data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting stock quote for {symbol}: {e}")
            return None
    
    def _fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Синхронная функция для получения данных через yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close else 0
            
            return {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'currency': info.get('currency', 'USD'),
                'name': info.get('longName', symbol),
                'market_cap': info.get('marketCap'),
                'volume': hist['Volume'].iloc[-1] if not hist.empty else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"_fetch_stock_data error: {e}")
            return None
    
    async def get_currency_rate(self, from_currency: str = "USD", to_currency: str = "RUB") -> Optional[Dict]:
        """
        Получить курс валют через ЦБ РФ или Yahoo Finance.
        """
        try:
            logger.info(f"🔍 Getting currency rate {from_currency}/{to_currency}")
            
            # Сначала пробуем ЦБ РФ для рублевых пар
            if to_currency == "RUB":
                cbr_data = await self._fetch_cbr_rate(from_currency)
                if cbr_data:
                    return cbr_data
            
            # Fallback на Yahoo Finance
            if YFINANCE_AVAILABLE:
                pair_symbol = f"{from_currency}{to_currency}=X"
                return await self.get_stock_quote(pair_symbol)
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting currency rate: {e}")
            return None
    
    async def _fetch_cbr_rate(self, currency: str) -> Optional[Dict]:
        """Получить курс валюты через ЦБ РФ."""
        try:
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
            response = await asyncio.to_thread(requests.get, url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if currency.upper() in data['Valute']:
                    valute_data = data['Valute'][currency.upper()]
                    rate = valute_data['Value']
                    prev_rate = valute_data['Previous']
                    
                    return {
                        'symbol': f"{currency}/RUB",
                        'price': round(rate, 4),
                        'change': round(rate - prev_rate, 4),
                        'change_percent': round(((rate - prev_rate) / prev_rate) * 100, 2),
                        'currency': 'RUB',
                        'name': valute_data['Name'],
                        'source': 'ЦБ РФ',
                        'timestamp': data['Date']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"ЦБ РФ API error: {e}")
            return None
    
    async def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """
        Получить цену криптовалюты через Yahoo Finance.
        """
        if not YFINANCE_AVAILABLE:
            return None
            
        try:
            # Криптовалюты на Yahoo Finance
            crypto_symbol = f"{symbol.upper()}-USD"
            return await self.get_stock_quote(crypto_symbol)
            
        except Exception as e:
            logger.error(f"Error getting crypto price for {symbol}: {e}")
            return None

# Глобальный экземпляр клиента (пока заглушка)
finance_client = FinanceDataClient()

# TODO: Функции для будущей интеграции

async def get_market_data(asset_type: str, symbol: str) -> Dict:
    """
    Универсальная функция получения рыночных данных.
    
    Args:
        asset_type: 'stock', 'currency', 'crypto', 'commodity'
        symbol: Символ актива
    
    Returns:
        Словарь с рыночными данными
    """
    logger.info(f"Market data requested: {asset_type}:{symbol} - PLACEHOLDER")
    
    return {
        'symbol': symbol,
        'asset_type': asset_type,
        'price': None,
        'change': None,
        'volume': None,
        'timestamp': datetime.now().isoformat(),
        'source': 'placeholder',
        'error': 'Finance APIs not implemented yet'
    }

def format_market_data(data: Dict) -> str:
    """
    Форматирование рыночных данных для LLM.
    """
    if data.get('error'):
        return f"⚠️ Данные по {data['symbol']} недоступны: {data['error']}"
    
    # TODO: Реализовать красивое форматирование когда будут реальные данные
    return f"📊 {data['symbol']}: цена недоступна (API не подключены)"
