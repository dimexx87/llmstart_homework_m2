#!/usr/bin/env python3
"""
LLM Assistant Telegram Bot - Entry Point
"""
import logging
import sys
import asyncio
import signal
from config import TELEGRAM_BOT_TOKEN, validate_config
from modules.bot import setup_bot
try:
    from modules.web_search import web_search_client
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    web_search_client = None
    WEB_SEARCH_AVAILABLE = False

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    # Закрываем web search сессию (если доступен)
    if WEB_SEARCH_AVAILABLE and web_search_client:
        try:
            asyncio.run(web_search_client.close())
        except Exception as e:
            logger.warning(f"Error closing web search client: {e}")
    sys.exit(0)

def main():
    """Main entry point for the bot."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Setup and start bot
        application = setup_bot(TELEGRAM_BOT_TOKEN)
        logger.info("Starting Telegram bot...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Start polling with increased timeouts
        application.run_polling(
            poll_interval=1.0,
            timeout=20,
            bootstrap_retries=3,
            read_timeout=60,
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=10
        )
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()