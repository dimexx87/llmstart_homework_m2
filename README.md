# LLM Финансовый Помощник

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](tests/)

Профессиональный Telegram-бот для финансового анализа с использованием LLM и актуальных рыночных данных из ЦБ РФ и Yahoo Finance.

## ✨ Возможности

- 🤖 **LLM Интеграция** - Работает на Claude Sonnet 4 через OpenRouter API
- 💰 **Реальные финансовые данные** - Курсы валют, акции, товары и криптовалюты
- 📊 **Множественные источники** - ЦБ РФ API, Yahoo Finance с умным резервированием
- 💬 **Память разговора** - Сохраняет контекст беседы для естественного общения
- 🐳 **Готов к продакшну** - Docker контейнеризация с проверками здоровья
- 🔒 **Безопасность** - Конфигурация через переменные окружения
- ✅ **Протестирован** - Полное покрытие unit-тестами

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- [Telegram Bot Token](https://core.telegram.org/bots#botfather)
- [OpenRouter API Key](https://openrouter.ai/)

### Установка

#### Вариант 1: Docker (Рекомендуется)

```bash
# Клонировать репозиторий
git clone <repository-url>
cd llm-financial-bot

# Настроить окружение
cp .env.example .env
# Отредактировать .env с вашими токенами

# Запустить с Docker
docker-compose up -d
```

#### Вариант 2: Локальная разработка

```bash
# Клонировать и настроить
git clone <repository-url>
cd llm-financial-bot
pip install -r requirements.txt

# Настроить окружение
cp .env.example .env
# Отредактировать .env с вашими токенами

# Запустить
python main.py
```

### Конфигурация

Создайте файл `.env`:

```env
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
OPENROUTER_API_KEY=ваш_openrouter_api_key
LOG_LEVEL=INFO
```

## 📱 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветственное сообщение и возможности бота |
| `/help` | Список доступных команд |
| `/clear` | Очистить историю текущего чата |
| **Текстовое сообщение** | Получить финансовый анализ с ИИ |

## 💡 Примеры использования

```
Пользователь: Какой сейчас курс доллара?
Бот: 💱 USD/RUB: 95.45 ₽ (+0.8%)
     Официальный курс ЦБ РФ на 09.01.2025

Пользователь: Как дела у акций Сбербанка?
Бот: 📈 SBER.ME: 255.30 ₽ (-1.2%)
     Крупнейший банк России показывает небольшое снижение...

Пользователь: Анализ цены биткоина
Бот: ₿ BTC-USD: $42,580 (+2.1%)
     Биткоин продолжает восходящий тренд...
```

## 🏗️ Архитектура

```
├── main.py                 # Точка входа приложения
├── config.py               # Конфигурация окружения
├── requirements.txt        # Python зависимости
├── Dockerfile             # Определение Docker контейнера
├── docker-compose.yml     # Оркестрация контейнеров
├── Makefile              # Команды разработки
├── build.ps1             # PowerShell скрипт для Windows
├── modules/
│   ├── bot.py            # Обработчики Telegram бота
│   ├── llm.py            # LLM интеграция и история чатов
│   ├── finance_data.py   # API финансовых данных
│   └── web_search.py     # Резервный веб-поиск
└── tests/                # Unit-тесты
    ├── test_config.py
    ├── test_finance_data.py
    └── test_llm.py
```

## 📊 Источники данных

- **🏦 Центральный банк РФ** - Официальные курсы USD/RUB, EUR/RUB
- **📈 Yahoo Finance** - Акции (SBER.ME), товары (GC=F), криптовалюты (BTC-USD)
- **🔍 Веб-поиск** - Резервный источник дополнительной финансовой информации
- **🛡️ Умное резервирование** - Плавная деградация при недоступности API

## 🔧 Разработка

### Запуск тестов

```bash
# Установить тестовые зависимости
pip install pytest pytest-asyncio

# Запустить тесты
python -m pytest tests/ -v
```

### Docker команды

```bash
# Собрать образ
docker build -t llm-telegram-bot .

# Запустить сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f bot

# Остановить сервисы
docker-compose down
```

### Команды разработки

**Linux/Mac:**
```bash
make help          # Показать доступные команды
make install       # Установить зависимости
make test          # Запустить тесты
make build         # Собрать Docker образ
```

**Windows:**
```powershell
.\build.ps1 help    # Показать доступные команды
.\build.ps1 install # Установить зависимости
.\build.ps1 test    # Запустить тесты
.\build.ps1 build   # Собрать Docker образ
```

## 🧪 Тестирование

Проект включает комплексные unit-тесты:

- Валидация конфигурации
- Получение финансовых данных
- Обработка LLM разговоров
- Управление историей чатов

```bash
python -m pytest tests/ -v
```

## 📋 Требования

### Python зависимости

- `python-telegram-bot==20.3` - Telegram Bot API
- `openai==1.51.0` - OpenRouter/OpenAI клиент
- `yfinance==0.2.28` - Данные Yahoo Finance
- `requests==2.31.0` - HTTP запросы
- `python-dotenv==1.0.0` - Управление окружением

### Системные требования

- **Память**: 512MB+ рекомендуется
- **Хранилище**: 100MB для приложения
- **Сеть**: Интернет-соединение для API

## 🔒 Безопасность

- Все чувствительные данные в переменных окружения
- Никаких захардкоженных API ключей или токенов
- Валидация входных данных и обработка ошибок
- Корректное завершение работы
- Непривилегированный пользователь в Docker

## 📝 Лицензия

Этот проект лицензирован под MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

## 🤝 Участие в разработке

1. Сделайте fork репозитория
2. Создайте ветку для функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Добавить потрясающую функцию'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

- 📧 **Проблемы**: [GitHub Issues](../../issues)
- 📖 **Документация**: Смотрите директорию `doc/`
- 🔧 **Разработка**: Смотрите `doc/vision.md`

---

**Создано с ❤️ для финансового сообщества**