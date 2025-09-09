"""
Tests for LLM module
"""
import pytest
from modules.llm import add_to_history, get_chat_context, clear_chat_history


def test_add_to_history():
    """Test adding message to chat history"""
    chat_id = 12345
    clear_chat_history(chat_id)  # Clean start
    
    add_to_history(chat_id, "user", "Hello")
    add_to_history(chat_id, "assistant", "Hi there")
    
    context = get_chat_context(chat_id)
    assert len(context) >= 2
    assert any(msg.get("role") == "user" for msg in context)


def test_get_chat_context():
    """Test getting chat context"""
    chat_id = 12346
    clear_chat_history(chat_id)  # Clean start
    
    add_to_history(chat_id, "user", "Test message")
    context = get_chat_context(chat_id)
    
    assert isinstance(context, list)
    assert len(context) >= 1


def test_clear_chat_history():
    """Test clearing chat history"""
    chat_id = 12347
    
    add_to_history(chat_id, "user", "Test")
    assert len(get_chat_context(chat_id)) >= 1
    
    clear_chat_history(chat_id)
    context = get_chat_context(chat_id)
    
    # Should be empty or have only system message
    assert len(context) <= 1


