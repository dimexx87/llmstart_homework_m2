# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an LLM-powered Telegram bot that provides customer consultation services. The bot integrates with OpenRouter API to generate intelligent responses based on a system prompt and conversation history. The project follows an iterative development approach with a monolithic architecture designed for simplicity and quick deployment.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file (copy from .env.example)
cp .env.example .env
# Then edit .env with your tokens:
# TELEGRAM_BOT_TOKEN=your_bot_token
# OPENROUTER_API_KEY=your_openrouter_key
```

### Running the Bot
```bash
# Run locally
python main.py

# Run with specific log level
LOG_LEVEL=DEBUG python main.py
```

### Testing
```bash
# When tests are implemented
pytest

# Run specific test file
pytest tests/test_bot.py -v
```

### Docker (Future Implementation)
```bash
# Build image
docker build -t llm-telegram-bot .

# Run with docker-compose
docker-compose up

# Run in background
docker-compose up -d
```

## Architecture

### Core Components

**Entry Point (`main.py`)**
- Validates configuration via environment variables
- Initializes and starts the Telegram bot application
- Handles graceful shutdown and error recovery

**Configuration (`config.py`)**
- Centralized environment variable management
- Validates required tokens (TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY)
- Supports LOG_LEVEL configuration

**Bot Logic (`modules/bot.py`)**
- Telegram bot handlers and command processing
- Currently implements `/start` command with welcome message
- Designed to handle text messages and integrate with LLM module

**LLM Integration (`modules/llm.py`)** - *Not yet implemented*
- Will handle OpenRouter API integration
- System prompt management and conversation history
- Context management (last 20 messages per user)

### Data Flow
1. User sends message → Telegram API → `bot.py`
2. `bot.py` processes command/text → calls `llm.py` (if needed)
3. `llm.py` sends request to OpenRouter → returns response
4. `bot.py` sends response back to user via Telegram

### Memory Architecture
- Conversation history stored in memory (`dict`: chat_id → message list)
- No persistent storage - history lost on bot restart
- Context limited to last 20 messages per conversation

## Development Principles

### KISS (Keep It Simple, Stupid)
- Simple, readable code without over-engineering
- Minimal abstractions and straightforward logic
- Direct integration patterns

### Iterative Development
According to `doc/tasklist.md`, development follows strict iterations:

1. **✅ Basic Bot** - Telegram bot with `/start` command and echo functionality
2. **⏳ LLM Integration** - OpenRouter API connection
3. **⏳ Conversation History** - In-memory context storage
4. **⏳ Error Handling** - Robust API error management
5. **⏳ Deployment** - Docker containerization

### Configuration Management
- All settings via environment variables
- Secrets: `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`
- Local development uses `.env` file (gitignored)
- Production uses container environment variables

## Key Files and Purposes

- `main.py` - Application entry point and bot lifecycle management
- `config.py` - Environment variable configuration and validation
- `modules/bot.py` - Telegram bot handlers and message processing
- `modules/llm.py` - OpenRouter API integration (to be implemented)
- `doc/vision.md` - Technical architecture and design decisions
- `doc/tasklist.md` - Development roadmap and iteration tracking
- `.cursor/rules/` - Development conventions and workflow guidelines

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather | - |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM | - |
| `LOG_LEVEL` | No | Logging level (INFO, DEBUG, ERROR) | INFO |

## Logging Strategy

- Standard Python `logging` module
- Levels: INFO (events), DEBUG (API calls), ERROR (failures)
- Output to stdout for Docker compatibility
- All LLM API requests/responses logged for monitoring

## Future Implementation Notes

When implementing the LLM module:
- System prompt should be defined as a constant
- Context includes system prompt + last 20 user messages
- Handle API timeouts and rate limiting gracefully
- Log all API interactions for quality monitoring

When adding Docker support:
- Simple Dockerfile with Python runtime
- `docker-compose.yml` for environment management
- Health checks and graceful shutdown handling

## Development Workflow

Follow the iterative workflow defined in `.cursor/rules/workflow.mdc`:
1. Select task from `doc/tasklist.md`
2. Implement following `doc/vision.md` architecture
3. Test functionality manually via Telegram
4. Update task status in tasklist
5. Commit with descriptive message format: `[iter#] description`
