# core/chatbot.py
# Updated to use send_message router
# Works with any provider

from config import config
from core.local_llm import send_message


SYSTEM_PROMPT = """You are AURA — AI-powered Universal Recognition Assistant.
You are intelligent, helpful, professional, and friendly.

Your capabilities include:
- Natural conversation and answering questions
- Explaining AI, technology, and general concepts
- Helping with document analysis and understanding
- Assisting with resume improvement and career guidance
- Providing insights about image and face analysis

Guidelines:
- Keep responses clear, concise, and helpful
- Be honest when you do not know something
- Use simple language unless technical detail is requested
- Format responses with bullet points when listing items
- Always be professional and encouraging"""


def chat(user_message, history=None):
    """
    Main chat function
    Uses whichever provider is configured
    """
    if not user_message or not user_message.strip():
        return False, None, "Empty message"

    user_message = user_message.strip()

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({
                    "role": role,
                    "content": content
                })

    messages.append({"role": "user", "content": user_message})

    # Use send_message router
    success, response, error = send_message(messages)

    if success:
        return True, response, None
    else:
        fallback = get_friendly_error(error)
        return False, fallback, error


def chat_with_context(user_message, system_override=None,
                       history=None, temperature=None):
    """
    Chat with custom system prompt
    """
    messages = []
    system = system_override or SYSTEM_PROMPT
    messages.append({"role": "system", "content": system})

    if history:
        for msg in history:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

    messages.append({"role": "user", "content": user_message})

    success, response, error = send_message(
        messages,
        temperature=temperature
    )

    if success:
        return True, response, None
    return False, f"⚠️ {error}", error


def get_friendly_error(error):
    """Return user friendly error message"""
    error_str = str(error).lower()

    if "groq" in error_str and "key" in error_str:
        return (
            "⚠️ Groq API key issue.\n\n"
            "Please check your GROQ_API_KEY in .env file.\n"
            "Get a free key at: console.groq.com"
        )
    elif "internet" in error_str or "connect" in error_str:
        return (
            "⚠️ No internet connection.\n\n"
            "Please check your internet and try again."
        )
    elif "rate limit" in error_str:
        return (
            "⚠️ Rate limit reached.\n\n"
            "Please wait a few seconds and try again."
        )
    elif "lm studio" in error_str or "1234" in error_str:
        return (
            "⚠️ Cannot connect to LM Studio.\n\n"
            "Switch to Groq API in your .env:\n"
            "LLM_PROVIDER=groq"
        )
    else:
        return (
            "⚠️ Something went wrong.\n\n"
            f"Error: {error}\n\n"
            "Please try again."
        )