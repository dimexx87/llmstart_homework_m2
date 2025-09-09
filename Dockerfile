# Dockerfile for LLM Assistant Telegram Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "main.py"]


