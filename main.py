import os
import sys
import json
import base64
import traceback
import io

# Windows encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Path fix — repo cloned into subfolder by Python Agent
_CWD = os.getcwd()
_HERE = os.path.dirname(os.path.abspath(__file__))

for _candidate in [_CWD, _HERE]:
    if os.path.isdir(os.path.join(_candidate, 'backend')):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break
    for _sub in os.listdir(_candidate):
        _subpath = os.path.join(_candidate, _sub)
        if os.path.isdir(_subpath) and os.path.isdir(os.path.join(_subpath, 'backend')):
            if _subpath not in sys.path:
                sys.path.insert(0, _subpath)
            break


def handle_message(msg, node_id=None):
    try:
        from dotenv import load_dotenv
        load_dotenv()

        config = msg.get("payload", {})
        if not config:
            msg["payload"] = {"error": "No configuration provided"}
            return msg

        required = ["topic", "objective", "audience", "duration"]
        missing  = [f for f in required if not config.get(f)]
        if missing:
            msg["payload"] = {"error": f"Missing required fields: {', '.join(missing)}"}
            return msg

        config = _parse_config(config)

        from backend.llm import generate_presentation_plan
        from backend.pptx_builder import build_pptx

        plan       = generate_presentation_plan(config)
        theme      = config.get("theme", "light")
        pptx_bytes = build_pptx(plan, theme=theme)

        topic_slug = config["topic"][:40].replace(" ", "_").replace("/", "-")
        filename   = f"NTT_DATA_{topic_slug}.pptx"

        msg["payload"] = {
            "status":   "success",
            "filename": filename,
            "pptx_b64": base64.b64encode(pptx_bytes).decode("utf-8")
        }

    except Exception as e:
        traceback.print_exc()
        msg["payload"] = {"error": str(e)}

    return msg


def _parse_config(config: dict) -> dict:
    duration_raw = config.get("duration", "15 Minutes")
    if "|" in duration_raw:
        parts = duration_raw.split("|", 1)
        config["duration"]    = parts[0].strip()
        config["slide_range"] = parts[1].strip()
    else:
        config["duration"]    = duration_raw
        config["slide_range"] = config.get("slide_range", "12-15")

    obj = config.get("objective", "")
    if obj == "custom":
        config["objective"] = config.get("objectiveCustomText", "Custom Objective")

    aud = config.get("audience", "")
    if aud == "custom":
        config["audience"] = config.get("audienceCustomText", "Mixed Audience")

    config["tech_level"]    = config.get("techLevel",    "Intermediate")
    config["speaker_notes"] = bool(config.get("speakerNotes", False))
    config["language"]      = config.get("language",     "English")
    config["theme"]         = config.get("theme",        "light")
    config["visuals"]       = config.get("visuals",      ["Automatically Decide"])

    return config
