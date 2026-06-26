import sys, os, json, base64, io

# Make the nttdata-ppt-gen package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nttdata-ppt-gen'))

from backend.llm import generate_presentation_plan
from backend.pptx_builder import build_pptx

def handle_message(msg, node_id):
    """
    Axetflow Python Agent entrypoint.
    msg.payload should be a dict with: topic, objective, audience, duration, theme, etc.
    Returns msg with payload = { "pptx_b64": "...", "filename": "..." }
    """
    try:
        config = msg.get("payload", {})
        if isinstance(config, str):
            config = json.loads(config)

        # Normalize fields (mirrors _parse_config from routes.py)
        duration_raw = config.get("duration", "15 Minutes")
        if "|" in duration_raw:
            parts = duration_raw.split("|", 1)
            config["duration"] = parts[0].strip()
            config["slide_range"] = parts[1].strip()
        else:
            config["duration"] = duration_raw
            config["slide_range"] = config.get("slide_range", "12-15")

        config["tech_level"]     = config.get("techLevel", "Intermediate")
        config["presenter_type"] = config.get("presenterType", "Technical Consultant")
        config["speaker_notes"]  = bool(config.get("speakerNotes", False))
        config["sections"]       = config.get("sections", [])
        config["language"]       = config.get("language", "English")
        config["theme"]          = config.get("theme", "light")
        config["visuals"]        = config.get("visuals", ["Automatically Decide"])

        # Two-stage LLM pipeline
        plan = generate_presentation_plan(config)

        # Build PPTX
        theme = config.get("theme", "light")
        pptx_bytes = build_pptx(plan, theme=theme)

        # Encode as base64 so it can travel through msg
        topic_slug = config["topic"][:40].replace(" ", "_").replace("/", "-")
        filename = f"NTT_DATA_{topic_slug}.pptx"

        msg["payload"] = {
            "success": True,
            "pptx_b64": base64.b64encode(pptx_bytes).decode("utf-8"),
            "filename": filename
        }

    except Exception as e:
        msg["payload"] = {"success": False, "error": str(e)}

    return msg
