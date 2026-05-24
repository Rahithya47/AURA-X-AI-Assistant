
# AURA-X AI Assistant

AURA-X is a local-first AI assistant for multimodal personal productivity and analysis. It combines document Q&A, face detection/recognition, emotion analysis, video/image understanding, resume generation, and an optional local LLM backend to provide privacy-focused, offline-capable AI features.

## Features

- Document chat (PDF / text Q&A)
- Face detection and recognition for people management
- Emotion analysis from images/video frames
- Video analysis and frame-level insights
- Resume builder and PDF generation
- Local LLM integration and memory management
- Vector store + Chroma DB support for semantic search

## Quick start

Requirements:

- Python 3.10+ (recommended)
- system dependencies for any native libraries used by packages in `requirements.txt`

Install and run:

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Initialize DB (if needed)
# Example: run the SQL in database/schema.sql with your preferred sqlite/mysql client

# Start the web app
python app.py

# Or run the debug chat server
python debug_chat.py
```

The app runs a local web server and serves pages from the `templates/` directory. Uploaded files and generated outputs are stored under `uploads/` and `generated/`.

## Project layout

- `app.py` — main Flask (or other framework) entrypoint for the web UI
- `config.py` — configuration options (edit for environment paths and keys)
- `core/` — core AI components and pipelines
	- `chatbot.py` — chat orchestration
	- `document_chat.py` — document ingestion and QA
	- `local_llm.py` — local LLM adapters
	- `memory_manager.py` — conversational memory handling
	- `face_detector.py`, `face_recognizer.py` — face pipelines
	- `image_understanding.py`, `video_analyzer.py`, `emotion_analyzer.py` — perception modules
- `database/` — DB helpers and vector store management
	- `schema.sql` — initial DB schema
	- `vector_store.py` — semantic indexing helpers
- `utils/` — utility modules (file handling, helpers, PDF generation)
- `templates/`, `static/` — frontend UI assets
- `uploads/` — incoming user files, images, videos, people
- `known_faces/` — store reference face images for recognition

## Typical workflows

- Document chat: upload PDF in the web UI (or place files under `uploads/documents/`), then use the Document Chat interface to ask questions; embeddings and vector search are used for retrieval.
- Face recognition: add reference images to `known_faces/` (one subfolder per person), then use the people management UI to enroll and label recognized faces.
- Resume builder: fill the form in the `resume_builder.html` UI, generate a formatted resume in `generated/resumes/`.

## Configuration & Models

- Place ML models (if required) in the `models/` folder (e.g., Haar cascades are already present: `models/haarcascade_frontalface_default.xml`).
- Edit `config.py` to point to local model files, change database paths, and set runtime flags (debug vs production).

## Development notes

- Tests: (none included by default) add unit tests for `core/` modules as needed.
- Formatting: use `black` / `isort` if configured in your environment.

## Troubleshooting

- If vector DB or embeddings fail, ensure `chroma_db/` has correct permissions and `requirements.txt` dependencies are installed.
- For face detection issues, verify `models/haarcascade_frontalface_default.xml` is present and readable.

## Contributing

Contributions are welcome. Please open issues or pull requests with clear descriptions and tests where appropriate.

## License

Specify your project license here.

---
Generated README for the AURA-X AI Assistant project.

