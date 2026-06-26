import json
import traceback
from flask import Blueprint, request, jsonify, send_file
import io

from backend.llm import generate_presentation_plan
from backend.pptx_builder import build_pptx

api_bp = Blueprint("api", __name__)


def _parse_config(config: dict) -> dict:
    """Normalise the raw form config from the frontend."""
    # Duration field arrives as "15 Minutes|12-15" — split into parts
    duration_raw = config.get("duration", "15 Minutes")
    if "|" in duration_raw:
        parts = duration_raw.split("|", 1)
        config["duration"]    = parts[0].strip()
        config["slide_range"] = parts[1].strip()
    else:
        config["duration"]    = duration_raw
        config["slide_range"] = config.get("slide_range", "12-15")

    # Normalise objective: handle "custom" selection
    obj = config.get("objective", "")
    if obj == "custom":
        config["objective"] = config.get("objectiveCustomText", "Custom Objective")

    # Normalise audience: handle "custom" selection
    aud = config.get("audience", "")
    if aud == "custom":
        config["audience"] = config.get("audienceCustomText", "Mixed Audience")

    # Map frontend field names to what the LLM expects
    config["tech_level"]     = config.get("techLevel",     "Intermediate")
    config["presenter_type"] = config.get("presenterType", "Technical Consultant")
    config["speaker_notes"]  = bool(config.get("speakerNotes", False))
    config["sections"]       = config.get("sections",      [])
    config["language"]       = config.get("language",      "English")
    config["theme"]          = config.get("theme",         "light")
    config["visuals"]        = config.get("visuals",       ["Automatically Decide"])

    return config


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "NTT DATA AI Presentation Generator"})


@api_bp.route("/generate", methods=["POST"])
def generate():
    """Accepts the form config, calls Groq, builds and returns .pptx."""
    try:
        config = request.get_json(force=True)
        if not config:
            return jsonify({"error": "No configuration provided"}), 400

        required = ["topic", "objective", "audience", "duration"]
        missing  = [f for f in required if not config.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        config = _parse_config(config)

        # Step 1 — get slide plan from Groq
        plan = generate_presentation_plan(config)

        # Step 2 — build .pptx
        theme   = config.get("theme", "light")
        pptx_bytes = build_pptx(plan, theme=theme)

        # Step 3 — stream file to client
        topic_slug = config["topic"][:40].replace(" ", "_").replace("/", "-")
        filename   = f"NTT_DATA_{topic_slug}.pptx"

        return send_file(
            io.BytesIO(pptx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=filename
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except json.JSONDecodeError as e:
        return jsonify({"error": f"LLM returned invalid JSON: {e}"}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@api_bp.route("/preview", methods=["POST"])
def preview():
    """
    Returns the raw slide plan JSON for front-end preview before download.
    """
    try:
        config = request.get_json(force=True)
        if not config:
            return jsonify({"error": "No configuration provided"}), 400

        plan = generate_presentation_plan(config)
        return jsonify({"success": True, "plan": plan})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
