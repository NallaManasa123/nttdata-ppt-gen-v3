from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import traceback
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

# ── helpers ────────────────────────────────────────────────────────────────

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


# ── routes ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok", "service": "NTT DATA AI Presentation Generator"})


@app.post("/api/generate")
async def generate(request: Request):
    try:
        from backend.llm import generate_presentation_plan
        from backend.pptx_builder import build_pptx

        config = await request.json()
        if not config:
            return JSONResponse({"error": "No configuration provided"}, status_code=400)

        required = ["topic", "objective", "audience", "duration"]
        missing  = [f for f in required if not config.get(f)]
        if missing:
            return JSONResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status_code=400)

        config     = _parse_config(config)
        plan       = generate_presentation_plan(config)
        theme      = config.get("theme", "light")
        pptx_bytes = build_pptx(plan, theme=theme)

        topic_slug = config["topic"][:40].replace(" ", "_").replace("/", "-")
        filename   = f"NTT_DATA_{topic_slug}.pptx"

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"LLM returned invalid JSON: {e}"}, status_code=500)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": f"Internal error: {str(e)}"}, status_code=500)


@app.post("/api/preview")
async def preview(request: Request):
    try:
        from backend.llm import generate_presentation_plan

        config = await request.json()
        if not config:
            return JSONResponse({"error": "No configuration provided"}, status_code=400)

        config = _parse_config(config)
        plan   = generate_presentation_plan(config)
        return JSONResponse({"success": True, "plan": plan})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


# ── frontend ───────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "templates", "index.html"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")),
    name="static"
)
