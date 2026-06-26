# NTT DATA AI Presentation Generator

AI-powered PowerPoint generator using Groq (llama-3.3-70b-versatile) and python-pptx,
built with Flask + vanilla HTML/CSS/JS.

---

## Project Structure

```
nttdata-ppt-gen/
├── app.py                          # Flask entry point
├── requirements.txt
├── .env                            # ← put your GROQ_API_KEY here
│
├── backend/
│   ├── __init__.py
│   ├── serve.py                    # serves frontend
│   ├── routes.py                   # API endpoints  /api/generate  /api/health
│   ├── llm.py                      # Groq client + prompt
│   ├── pptx_builder.py             # python-pptx slide builder
│   └── ntt_template.pptx           # original NTT DATA template (reference)
│
└── frontend/
    ├── templates/
    │   └── index.html              # main UI (5-step form)
    └── static/
        ├── css/
        │   └── style.css
        ├── js/
        │   └── app.js
        └── assets/
            ├── ntt_logo_blue.png   # logo for light slides / browser tab
            └── ntt_logo_white.png  # logo for dark slides / header
```

---

## Quick Start

### 1. Clone / unzip and enter the project folder
```bash
cd nttdata-ppt-gen
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your Groq API key
Edit `.env`:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
FLASK_PORT=5000
FLASK_DEBUG=false
```

Get a free key at https://console.groq.com

### 5. Run
```bash
python app.py
```

Open http://localhost:5000

---

## API Endpoints

| Method | Path             | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/`              | Main UI                              |
| GET    | `/api/health`    | Health check                         |
| POST   | `/api/generate`  | Generate + download .pptx            |
| POST   | `/api/preview`   | Return raw JSON slide plan           |

### POST /api/generate  — request body
```json
{
  "topic":          "Generative AI in SAP",
  "objective":      "Knowledge Transfer (KT)",
  "audience":       "Developers",
  "duration":       "15 Minutes",
  "slide_range":    "12-15",
  "presenter_type": "Technical Consultant",
  "tech_level":     "Advanced",
  "theme":          "dark",
  "style":          "Professional",
  "content_depth":  "Standard",
  "language":       "English",
  "speaker_notes":  true,
  "visuals":        ["Architecture Diagram", "Flowchart"],
  "sections":       ["Agenda", "Executive Summary", "Proposed Solution", "Thank You"]
}
```

Returns: `application/vnd.openxmlformats-officedocument.presentationml.presentation` (file download)

---

## VS Code — Recommended Extensions
- Python (ms-python.python)
- Pylance
- REST Client (for testing API endpoints)

---

## Notes
- The PPTX builder uses python-pptx with blank slide layouts and draws everything manually
  to ensure full NTT DATA brand compliance (no clashing template placeholders).
- The white logo (`ntt_logo_white.png`) is used on dark/blue header backgrounds.
- The blue logo (`ntt_logo_blue.png`) is used on light slide backgrounds and the browser tab.
- Visual placeholders (architecture diagrams, flowcharts etc.) appear as labelled boxes
  in the PPTX — replace with actual diagrams in PowerPoint as needed.
