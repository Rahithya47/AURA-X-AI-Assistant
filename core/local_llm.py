# core/local_llm.py
# Multi-provider LLM support
# Supports: Groq, OpenAI, Gemini, LM Studio
# Automatically picks based on .env settings

import requests
import json
from config import config


# ═══════════════════════════════════════════════════
# GROQ PROVIDER
# ═══════════════════════════════════════════════════

def send_to_groq(messages, temperature=None, max_tokens=None):
    """
    Send messages to Groq API
    
    FREE tier available at console.groq.com
    Supports: LLaMA 3.1, Mistral, Gemma, DeepSeek
    Speed: Extremely fast (fastest inference available)
    
    Args:
        messages: list of message dicts
        temperature: 0.0 to 1.0
        max_tokens: max response length
    
    Returns:
        (success, response_text, error)
    """
    if not config.GROQ_API_KEY:
        return False, None, (
            "Groq API key not set. "
            "Add GROQ_API_KEY to your .env file. "
            "Get free key at: console.groq.com"
        )

    if temperature is None:
        temperature = config.LM_STUDIO_TEMPERATURE
    if max_tokens is None:
        max_tokens = config.LM_STUDIO_MAX_TOKENS

    url = f"{config.GROQ_BASE_URL}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.GROQ_API_KEY}"
    }

    payload = {
        "model": config.GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    try:
        print(f"🌐 Sending to Groq ({config.GROQ_MODEL})...")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if content:
                print(f"✅ Groq response received")
                return True, content, None
            else:
                return False, None, "Empty response from Groq"

        elif response.status_code == 401:
            return False, None, (
                "Invalid Groq API key. "
                "Check your GROQ_API_KEY in .env file."
            )
        elif response.status_code == 429:
            return False, None, (
                "Groq rate limit reached. "
                "Wait a moment and try again."
            )
        else:
            error = response.text[:300]
            print(f"❌ Groq error {response.status_code}: {error}")
            return False, None, f"Groq error: {error}"

    except requests.exceptions.ConnectionError:
        return False, None, (
            "Cannot connect to Groq API. "
            "Check your internet connection."
        )
    except requests.exceptions.Timeout:
        return False, None, "Groq request timed out. Try again."
    except Exception as e:
        return False, None, f"Groq error: {str(e)}"


def check_groq_connection():
    """
    Check if Groq API is accessible
    Returns: (is_working, model_name, error)
    """
    if not config.GROQ_API_KEY:
        return False, None, "No API key set"

    try:
        url = f"{config.GROQ_BASE_URL}/models"
        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}"
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return True, config.GROQ_MODEL, None
        else:
            return False, None, f"Status: {response.status_code}"

    except requests.exceptions.ConnectionError:
        return False, None, "No internet connection"
    except Exception as e:
        return False, None, str(e)


# ═══════════════════════════════════════════════════
# OPENAI PROVIDER
# ═══════════════════════════════════════════════════

def send_to_openai(messages, temperature=None, max_tokens=None):
    """
    Send messages to OpenAI API
    
    Paid but very cheap for small usage
    Best quality responses
    """
    if not config.OPENAI_API_KEY:
        return False, None, (
            "OpenAI API key not set. "
            "Add OPENAI_API_KEY to your .env file."
        )

    if temperature is None:
        temperature = 0.7
    if max_tokens is None:
        max_tokens = 1024

    url = f"{config.OPENAI_BASE_URL}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    }

    payload = {
        "model": config.OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        print(f"🌐 Sending to OpenAI ({config.OPENAI_MODEL})...")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if content:
                print("✅ OpenAI response received")
                return True, content, None
            return False, None, "Empty response"

        elif response.status_code == 401:
            return False, None, "Invalid OpenAI API key"
        elif response.status_code == 429:
            return False, None, "OpenAI rate limit or quota exceeded"
        else:
            return False, None, f"OpenAI error: {response.text[:200]}"

    except requests.exceptions.ConnectionError:
        return False, None, "Cannot connect to OpenAI"
    except Exception as e:
        return False, None, f"OpenAI error: {str(e)}"


# ═══════════════════════════════════════════════════
# GEMINI PROVIDER
# ═══════════════════════════════════════════════════

def send_to_gemini(messages, temperature=None, max_tokens=None):
    """
    Send messages to Google Gemini API
    
    FREE tier: 60 requests per minute
    Great quality, fast responses
    """
    if not config.GEMINI_API_KEY:
        return False, None, (
            "Gemini API key not set. "
            "Add GEMINI_API_KEY to your .env file. "
            "Get free key at: makersuite.google.com"
        )

    if temperature is None:
        temperature = 0.7
    if max_tokens is None:
        max_tokens = 1024

    model = config.GEMINI_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
        f"?key={config.GEMINI_API_KEY}"
    )

    # Convert messages to Gemini format
    # Gemini uses different format than OpenAI
    gemini_contents = []
    system_text = ""

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "system":
            system_text = content
        elif role == "user":
            text = content
            if system_text and not gemini_contents:
                text = f"{system_text}\n\n{content}"
                system_text = ""
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": text}]
            })
        elif role == "assistant":
            gemini_contents.append({
                "role": "model",
                "parts": [{"text": content}]
            })

    if not gemini_contents:
        return False, None, "No messages to send"

    payload = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    try:
        print(f"🌐 Sending to Gemini ({model})...")

        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])

            if candidates:
                parts = (
                    candidates[0]
                    .get("content", {})
                    .get("parts", [])
                )
                if parts:
                    content = parts[0].get("text", "").strip()
                    if content:
                        print("✅ Gemini response received")
                        return True, content, None

            return False, None, "Empty response from Gemini"

        elif response.status_code == 400:
            return False, None, (
                "Gemini request error. "
                "Check your API key and model name."
            )
        elif response.status_code == 429:
            return False, None, (
                "Gemini rate limit reached. Wait a moment."
            )
        else:
            return False, None, (
                f"Gemini error {response.status_code}: "
                f"{response.text[:200]}"
            )

    except requests.exceptions.ConnectionError:
        return False, None, "Cannot connect to Gemini API"
    except Exception as e:
        return False, None, f"Gemini error: {str(e)}"


def check_gemini_connection():
    """Check if Gemini API is accessible"""
    if not config.GEMINI_API_KEY:
        return False, None, "No API key set"

    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models?key={config.GEMINI_API_KEY}"
        )
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, config.GEMINI_MODEL, None
        return False, None, f"Status: {response.status_code}"
    except Exception as e:
        return False, None, str(e)


# ═══════════════════════════════════════════════════
# LM STUDIO PROVIDER (Local)
# ═══════════════════════════════════════════════════

def send_to_lm_studio(messages, temperature=None,
                       max_tokens=None):
    """
    Send to LM Studio (local model)
    Fallback when cloud APIs not available
    """
    if temperature is None:
        temperature = 0.7
    if max_tokens is None:
        max_tokens = 1024

    base_url = config.LM_STUDIO_BASE_URL.rstrip("/")
    url = f"{base_url}/chat/completions"

    payload = {
        "model": config.LM_STUDIO_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    try:
        print(f"🏠 Sending to LM Studio...")
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if content:
                print("✅ LM Studio response received")
                return True, content, None
            return False, None, "Empty response"

        else:
            return False, None, (
                f"LM Studio error: {response.status_code}"
            )

    except requests.exceptions.ConnectionError:
        return False, None, (
            "LM Studio not running. "
            "Start LM Studio or use a cloud provider."
        )
    except requests.exceptions.Timeout:
        return False, None, "LM Studio timeout"
    except Exception as e:
        return False, None, str(e)


def check_lm_studio_connection():
    """Check LM Studio connection"""
    try:
        base_url = config.LM_STUDIO_BASE_URL.rstrip("/")
        url = f"{base_url}/models"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            models = response.json().get("data", [])
            if models:
                return True, models[0].get("id"), None
            return True, "No model loaded", None
        return False, None, f"Status: {response.status_code}"
    except Exception as e:
        return False, None, str(e)


def get_available_models():
    """Get available models from current provider"""
    provider = config.LLM_PROVIDER

    if provider == "groq":
        is_ok, _, _ = check_groq_connection()
        if is_ok:
            return [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
    elif provider == "lmstudio":
        try:
            base_url = config.LM_STUDIO_BASE_URL.rstrip("/")
            r = requests.get(f"{base_url}/models", timeout=3)
            if r.status_code == 200:
                return [
                    m.get("id")
                    for m in r.json().get("data", [])
                ]
        except Exception:
            pass
    return []


# ═══════════════════════════════════════════════════
# MAIN ROUTER — Picks the right provider
# ═══════════════════════════════════════════════════

def send_message(messages, temperature=None, max_tokens=None):
    """
    MAIN FUNCTION - Called by chatbot.py
    
    Automatically routes to correct provider
    based on LLM_PROVIDER setting in .env
    
    Priority:
    1. Whatever is set in LLM_PROVIDER
    2. Falls back to next available provider
    3. Shows helpful error if all fail
    
    Args:
        messages: list of message dicts
        temperature: 0.0 to 1.0
        max_tokens: max response tokens
    
    Returns:
        (success, response_text, error)
    """
    provider = config.LLM_PROVIDER.lower().strip()

    print(f"\n🤖 LLM Provider: {provider.upper()}")

    # ─── Route to Provider ───
    if provider == "groq":
        success, response, error = send_to_groq(
            messages, temperature, max_tokens
        )

    elif provider == "openai":
        success, response, error = send_to_openai(
            messages, temperature, max_tokens
        )

    elif provider == "gemini":
        success, response, error = send_to_gemini(
            messages, temperature, max_tokens
        )

    elif provider == "lmstudio":
        success, response, error = send_to_lm_studio(
            messages, temperature, max_tokens
        )

    else:
        # Unknown provider, try Groq first
        print(f"⚠️ Unknown provider: {provider}, trying Groq...")
        success, response, error = send_to_groq(
            messages, temperature, max_tokens
        )

    # ─── If Primary Fails, Try Fallbacks ───
    if not success:
        print(f"⚠️ Primary provider failed: {error}")
        print("🔄 Trying fallback providers...")

        # Try each fallback in order
        fallbacks = []

        if provider != "groq" and config.GROQ_API_KEY:
            fallbacks.append(("groq", send_to_groq))
        if provider != "openai" and config.OPENAI_API_KEY:
            fallbacks.append(("openai", send_to_openai))
        if provider != "gemini" and config.GEMINI_API_KEY:
            fallbacks.append(("gemini", send_to_gemini))
        if provider != "lmstudio":
            fallbacks.append(("lmstudio", send_to_lm_studio))

        for fallback_name, fallback_fn in fallbacks:
            print(f"   Trying {fallback_name}...")
            fb_success, fb_response, fb_error = fallback_fn(
                messages, temperature, max_tokens
            )
            if fb_success:
                print(f"✅ Fallback worked: {fallback_name}")
                return True, fb_response, None

        # All providers failed
        return False, None, error

    return True, response, None


def get_provider_status():
    """
    Get status of all configured providers
    Used by health check endpoint
    """
    status = {}
    provider = config.LLM_PROVIDER

    # Check primary provider
    if provider == "groq":
        ok, model, err = check_groq_connection()
        status["groq"] = {
            "active": True,
            "connected": ok,
            "model": model or config.GROQ_MODEL,
            "error": err,
            "free": True
        }
    elif provider == "lmstudio":
        ok, model, err = check_lm_studio_connection()
        status["lmstudio"] = {
            "active": True,
            "connected": ok,
            "model": model or config.LM_STUDIO_MODEL,
            "error": err,
            "free": True
        }
    elif provider == "gemini":
        ok, model, err = check_gemini_connection()
        status["gemini"] = {
            "active": True,
            "connected": ok,
            "model": model or config.GEMINI_MODEL,
            "error": err,
            "free": True
        }
    elif provider == "openai":
        status["openai"] = {
            "active": True,
            "connected": bool(config.OPENAI_API_KEY),
            "model": config.OPENAI_MODEL,
            "error": None if config.OPENAI_API_KEY else "No key",
            "free": False
        }

    status["current_provider"] = provider
    return status