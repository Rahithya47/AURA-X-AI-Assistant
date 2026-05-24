# app.py
# Main Flask application for AURA-X-AI-ASSISTANT
# Phase 2: Added Chat API routes

import os
from flask import Flask, render_template, jsonify, request
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config, get_all_required_folders
from database.db_manager import init_db
from utils.file_handler import ensure_folders_exist
from utils.helpers import success_response, error_response


def create_app():
    """
    Application factory function
    Creates and configures Flask app
    """
    app = Flask(__name__)

    # ─────────────────────────────────────────
    # Flask Configuration
    # ─────────────────────────────────────────
    app.secret_key = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["DEBUG"] = config.DEBUG

    # Enable CORS
    CORS(app)

    # ─────────────────────────────────────────
    # Create Required Folders
    # ─────────────────────────────────────────
    for folder in get_all_required_folders():
        os.makedirs(folder, exist_ok=True)

    ensure_folders_exist()

    # ─────────────────────────────────────────
    # Initialize Database
    # ─────────────────────────────────────────
    init_db()

    # ═══════════════════════════════════════════
    # PAGE ROUTES
    # ═══════════════════════════════════════════

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/document-chat")
    def document_chat_page():
        return render_template("document_chat.html")

    @app.route("/resume-builder")
    def resume_builder_page():
        return render_template("resume_builder.html")

    @app.route("/manage-people")
    def manage_people_page():
        return render_template("manage_people.html")

    # ═══════════════════════════════════════════
    # HEALTH CHECK
    # ═══════════════════════════════════════════

    @app.route("/api/health")
    def health_check():
        """Check app and LM Studio status"""
        from core.local_llm import check_lm_studio_connection
        
        lm_running, model_name, lm_error = check_lm_studio_connection()
        
        return jsonify({
            "status": "healthy",
            "app": "AURA-X-AI-ASSISTANT",
            "version": "1.0.0",
            "lm_studio": {
                "running": lm_running,
                "url": config.LM_STUDIO_BASE_URL,
                "model": model_name or config.LM_STUDIO_MODEL,
                "error": lm_error
            }
        })

    # ═══════════════════════════════════════════
    # CHAT API ROUTES
    # ═══════════════════════════════════════════

    @app.route("/api/chat", methods=["POST"])
    def chat_api():
        """
        Main chat endpoint
        
        Request body:
        {
            "message": "user's message",
            "session_id": "session_abc123"
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "response": "AI reply...",
                "session_id": "session_abc123"
            }
        }
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return jsonify(
                    error_response("No data received", 400)
                )

            message = data.get("message", "").strip()
            session_id = data.get("session_id", "")

            # Validate message
            if not message:
                return jsonify(
                    error_response("Message cannot be empty", 400)
                )

            if len(message) > 5000:
                return jsonify(
                    error_response("Message too long (max 5000 chars)", 400)
                )

            # Import here to avoid circular imports
            from core.chatbot import chat
            from core.memory_manager import (
                ensure_session_exists,
                get_history_for_llm,
                add_user_message,
                add_assistant_message
            )
            from database.db_manager import update_session_title

            # Ensure session exists
            session_id = ensure_session_exists(session_id)

            # Get conversation history
            history = get_history_for_llm(session_id)

            # Save user message to database
            add_user_message(session_id, message)

            # Update session title from first message
            from database.db_manager import get_message_count
            msg_count = get_message_count(session_id)
            if msg_count <= 1:
                update_session_title(session_id, message)

            # Get AI response
            success, response_text, error = chat(message, history)

            # Save assistant response
            if response_text:
                add_assistant_message(session_id, response_text)

            return jsonify(success_response(
                data={
                    "response": response_text,
                    "session_id": session_id,
                    "success": success
                },
                message="Response generated"
            ))

        except Exception as e:
            print(f"❌ Chat API error: {e}")
            return jsonify(
                error_response(f"Server error: {str(e)}", 500)
            )

    @app.route("/api/chat/clear", methods=["POST"])
    def clear_chat_api():
        """
        Clear chat history for a session
        
        Request body:
        { "session_id": "session_abc123" }
        """
        try:
            data = request.get_json()
            session_id = data.get("session_id", "") if data else ""

            if not session_id:
                return jsonify(
                    error_response("Session ID required", 400)
                )

            from core.memory_manager import clear_conversation
            result = clear_conversation(session_id)

            if result:
                return jsonify(success_response(
                    message="Chat history cleared"
                ))
            else:
                return jsonify(
                    error_response("Failed to clear history", 500)
                )

        except Exception as e:
            return jsonify(error_response(str(e), 500))

    @app.route("/api/chat/history/<session_id>")
    def get_chat_history(session_id):
        """
        Get full chat history for a session
        """
        try:
            from core.memory_manager import get_conversation_history
            messages = get_conversation_history(session_id, limit=50)

            return jsonify(success_response(
                data={"messages": messages, "session_id": session_id}
            ))

        except Exception as e:
            return jsonify(error_response(str(e), 500))

    @app.route("/api/lm-status")
    def lm_status():
        """
        Check LM Studio connection status
        """
        from core.local_llm import (
            check_lm_studio_connection,
            get_available_models
        )
        
        is_running, model, error = check_lm_studio_connection()
        models = get_available_models() if is_running else []

        return jsonify({
            "running": is_running,
            "model": model,
            "models": models,
            "url": config.LM_STUDIO_BASE_URL,
            "error": error
        })

    # ═══════════════════════════════════════════
    # IMAGE API ROUTES (placeholder for Phase 3)
    # ═══════════════════════════════════════════

    # REPLACE the analyze_image_api route in app.py with this:
    # ═══════════════════════════════════════════
    # IMAGE API ROUTES
    # ═══════════════════════════════════════════

    @app.route("/api/analyze-image", methods=["POST"])
    def analyze_image_api():
        try:
            if "image" not in request.files:
                return jsonify(
                    error_response("No image file provided", 400)
                )

            file = request.files["image"]

            if not file or file.filename == "":
                return jsonify(
                    error_response("No file selected", 400)
                )

            from utils.file_handler import allowed_file, save_uploaded_file

            if not allowed_file(file.filename, "image"):
                return jsonify(error_response(
                    "Invalid file type. Allowed: JPG, PNG, JPEG, WEBP",
                    400
                ))

            success, file_path, filename, save_error = save_uploaded_file(
                file, "images"
            )

            if not success:
                return jsonify(
                    error_response(f"Could not save file: {save_error}", 500)
                )

            print(f"📸 Image uploaded: {filename}")

            from core.image_understanding import understand_image
            result = understand_image(file_path)

            from database.db_manager import save_image_analysis
            save_image_analysis(filename, file_path, result)

            return jsonify(success_response(
                data=result,
                message=result.get("summary", "Analysis complete")
            ))

        except Exception as e:
            print(f"❌ Image API error: {e}")
            import traceback
            traceback.print_exc()

            return jsonify(error_response(
                f"Image analysis failed: {str(e)}", 500
            ))


    @app.route("/uploads/<path:filename>")
    def serve_uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory("uploads", filename)


    @app.route("/api/image-history")
    def image_history_api():
        try:
            from database.db_manager import get_image_history
            history = get_image_history(limit=10)

            return jsonify(success_response(
                data={"history": history}
            ))

        except Exception as e:
            return jsonify(error_response(str(e), 500))



# # ADD THIS NEW ROUTE for serving uploaded images
# @app.route("/uploads/<path:filename>")
# def serve_uploaded_file(filename):
#     """Serve uploaded files (images, documents etc)"""
#     from flask import send_from_directory
#     return send_from_directory("uploads", filename)


# ADD THIS ROUTE for image analysis history
    # @app.route("/api/image-history")
    # def image_history_api():
    #     """Get recent image analysis history"""
    #     try:
    #         from database.db_manager import get_image_history
    #         history = get_image_history(limit=10)
    #         return jsonify(success_response(
    #             data={"history": history}
    #         ))
    #     except Exception as e:
    #         return jsonify(error_response(str(e), 500))

    # ═══════════════════════════════════════════
    # DOCUMENT API ROUTES (placeholder for Phase 4)
    # ═══════════════════════════════════════════

    @app.route("/api/upload-document", methods=["POST"])
    def upload_document_api():
        """Document upload - Full implementation in Phase 4"""
        return jsonify(error_response(
            "Document chat coming in Phase 4", 501
        ))

    @app.route("/api/document-chat", methods=["POST"])
    def document_chat_api():
        """Document chat - Full implementation in Phase 4"""
        return jsonify(error_response(
            "Document chat coming in Phase 4", 501
        ))

    # ═══════════════════════════════════════════
    # RESUME API ROUTES (placeholder for Phase 5)
    # ═══════════════════════════════════════════

    @app.route("/api/analyze-resume", methods=["POST"])
    def analyze_resume_api():
        """Resume analysis - Full implementation in Phase 5"""
        return jsonify(error_response(
            "Resume builder coming in Phase 5", 501
        ))

    # ═══════════════════════════════════════════
    # PEOPLE API ROUTES (placeholder for Phase 6)
    # ═══════════════════════════════════════════

    @app.route("/api/people/add", methods=["POST"])
    def add_person_api():
        """Add person - Full implementation in Phase 6"""
        return jsonify(error_response(
            "People management coming in Phase 6", 501
        ))

    @app.route("/api/people/list")
    def list_people_api():
        """List people - Full implementation in Phase 6"""
        return jsonify(success_response(
            data={"people": []},
            message="People management coming in Phase 6"
        ))

    @app.route("/api/people/delete/<person_id>", methods=["DELETE"])
    def delete_person_api(person_id):
        """Delete person - Full implementation in Phase 6"""
        return jsonify(error_response(
            "People management coming in Phase 6", 501
        ))

    # ═══════════════════════════════════════════
    # ERROR HANDLERS
    # ═══════════════════════════════════════════

    @app.errorhandler(404)
    def not_found(error):
        return render_template("index.html"), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "status": "error",
            "message": f"File too large. Max size: "
                       f"{config.MAX_UPLOAD_SIZE_MB}MB"
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

    print("✅ AURA-X app created successfully")
    print(f"🤖 LM Studio URL: {config.LM_STUDIO_BASE_URL}")
    print(f"🧠 Model: {config.LM_STUDIO_MODEL}")

    return app


# ─────────────────────────────────────────
# Run Application
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 50)
    print("🚀 AURA-X AI Assistant Starting...")
    print(f"🌐 Open: http://localhost:{config.PORT}")
    print("=" * 50 + "\n")
    app.run(
        debug=config.DEBUG,
        port=config.PORT,
        host="0.0.0.0"
    )