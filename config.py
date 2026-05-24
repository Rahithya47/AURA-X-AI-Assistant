# config.py
# Updated with multi-provider support

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ─────────────────────────────────────────
    # Flask Settings
    # ─────────────────────────────────────────
    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY",
        "aura-x-default-secret-key"
    )
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    PORT = int(os.getenv("FLASK_PORT", 5000))

    # ─────────────────────────────────────────
    # LLM Provider
    # Options: groq, openai, lmstudio, gemini
    # ─────────────────────────────────────────
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

    # ─────────────────────────────────────────
    # Groq Settings
    # ─────────────────────────────────────────
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    # ─────────────────────────────────────────
    # OpenAI Settings
    # ─────────────────────────────────────────
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_BASE_URL = "https://api.openai.com/v1"

    # ─────────────────────────────────────────
    # Gemini Settings
    # ─────────────────────────────────────────
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-1.5-flash"
    )

    # ─────────────────────────────────────────
    # LM Studio Settings (local fallback)
    # ─────────────────────────────────────────
    LM_STUDIO_BASE_URL = os.getenv(
        "LM_STUDIO_BASE_URL",
        "http://localhost:1234/v1"
    )
    LM_STUDIO_MODEL = os.getenv(
        "LM_STUDIO_MODEL",
        "local-model"
    )

    # ─────────────────────────────────────────
    # Common LLM Settings
    # ─────────────────────────────────────────
    LM_STUDIO_TEMPERATURE = 0.7
    LM_STUDIO_MAX_TOKENS = 1024
    LM_STUDIO_TIMEOUT = 60

    # ─────────────────────────────────────────
    # Database Settings
    # ─────────────────────────────────────────
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        "data/aura.db"
    )
    CHROMA_DB_PATH = os.getenv(
        "CHROMA_DB_PATH",
        "data/chroma_db"
    )

    # ─────────────────────────────────────────
    # Upload Settings
    # ─────────────────────────────────────────
    BASE_UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "uploads"
    )
    MAX_UPLOAD_SIZE_MB = int(
        os.getenv("MAX_UPLOAD_SIZE_MB", 16)
    )
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    UPLOAD_FOLDERS = {
        "images": "uploads/images",
        "documents": "uploads/documents",
        "resumes": "uploads/resumes",
        "videos": "uploads/videos",
        "people": "uploads/people"
    }

    # ─────────────────────────────────────────
    # File Extensions
    # ─────────────────────────────────────────
    ALLOWED_IMAGE_EXTENSIONS = {
        "jpg", "jpeg", "png", "webp", "gif", "bmp"
    }
    ALLOWED_DOCUMENT_EXTENSIONS = {
        "pdf", "docx", "doc", "txt"
    }
    ALLOWED_RESUME_EXTENSIONS = {
        "pdf", "docx", "doc", "txt"
    }
    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4", "avi", "mov", "mkv", "webm"
    }

    # ─────────────────────────────────────────
    # Model Paths
    # ─────────────────────────────────────────
    MODELS_FOLDER = "models"
    HAARCASCADE_PATH = os.path.join(
        MODELS_FOLDER,
        "haarcascade_frontalface_default.xml"
    )
    KNOWN_FACES_FOLDER = "known_faces"
    GENERATED_FOLDER = "generated"
    GENERATED_REPORTS = "generated/reports"
    GENERATED_RESUMES = "generated/resumes"

    # ─────────────────────────────────────────
    # Chat Settings
    # ─────────────────────────────────────────
    CHAT_HISTORY_LIMIT = 10

    # ─────────────────────────────────────────
    # AURA System Prompt
    # ─────────────────────────────────────────
    AURA_SYSTEM_PROMPT = """You are AURA — AI-powered Universal Recognition Assistant.
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


config = Config()


def get_all_required_folders():
    """Return list of all folders that must exist"""
    return [
        "data",
        "data/chroma_db",
        "uploads",
        "uploads/images",
        "uploads/documents",
        "uploads/resumes",
        "uploads/videos",
        "uploads/people",
        "models",
        "known_faces",
        "generated",
        "generated/reports",
        "generated/resumes",
        "static/css",
        "static/js",
        "templates",
        "core",
        "database",
        "utils"
    ]