import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenRouter API Configuration  
OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

def validate_config() -> None:
    """Validate required configuration parameters."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")
