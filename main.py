#!/usr/bin/env python3
"""
LLM Assistant Telegram Bot - Entry Point
"""
import logging
import sys
from config import TELEGRAM_BOT_TOKEN, validate_config
from modules.bot import setup_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the bot."""
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Setup and start bot
        application = setup_bot(TELEGRAM_BOT_TOKEN)
        logger.info("Starting Telegram bot...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Start polling
        application.run_polling(
            poll_interval=0.0,
            timeout=10,
            bootstrap_retries=-1,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=1
        )
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()