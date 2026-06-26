"""
NTT DATA AI Presentation Generator — Two-Stage Groq Pipeline v2
Implements: AI Decision Engine, Visual Intelligence, Section Selection, Content Density.
"""
import os, json, re
from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=api_key)
    return _client

def _clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    idx = raw.find("{")
    if idx > 0: raw = raw[idx:]
    last = max(raw.rfind("}"), raw.rfind("]"))
    if last != -1: raw = raw[:last+1]
    return raw

def _call_groq(system: str, user: str, max_tokens: int = 7000) -> str:
    client = get_client()
    model  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    resp   = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.6,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 — BLUEPRINT WITH AI DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════════════
STAGE1_SYSTEM = """You are an elite NTT DATA Senior Presentation Architect with 15 years of consulting experience.

YOUR JOB: Before planning slides, run the AI DECISION ENGINE on every potential slide:
1. Is this the best layout for this content type?
2. Is a diagram more effective than bullets here?
3. Which visual best explains this specific topic?
4. Does this slide connect logically to the next?
5. Will this slide have balanced whitespace, or will it look empty?

VISUAL INTELLIGENCE RULES:
- Processes, workflows, pipelines → process_flow
- System/solution/cloud architecture → architecture
- Decision logic, approval flows → flowchart
- Project phases, sprints, milestones → timeline
- Feature comparison, options analysis → comparison_table
- Business health, metrics, outcomes → kpi_cards
- Benefits, features list (2 categories) → two_column_cards
- Strategic categories (low/mid/high) → pyramid
- Circular processes, DevOps loops → cycle
- Org structures, component hierarchy → hierarchy
- Multi-quarter delivery plan → roadmap
- SWOT, gap analysis → swot
- Numbered sections → agenda

SECTION INTELLIGENCE: Only include sections that genuinely serve the topic.
For SAP Migration: Current Landscape, Target Architecture, Migration Strategy, Roadmap, Risks
For AI/ML: Business Problem, Solution Overview, Model Architecture, Pipeline, Use Cases, Benefits
For Cloud: Current State, Cloud Strategy, Architecture, Migration Plan, Cost Model, Governance
For Business Case: Executive Summary, Market Analysis, Solution, ROI, Implementation, Risk
NEVER auto-add SWOT or Future Scope unless they add real value to this specific topic.

STORY FLOW (non-negotiable):
Cover (1) → Agenda (2) → [Context/Problem slides] → [Solution slides] → [Technical slides] → [Benefits/ROI] → [Roadmap/Next Steps] → Closing (last)

VISUAL-FIRST PRINCIPLE: Before assigning "bullet_list" layout, ask: "Is a diagram available for this content?"
If ANY of these apply → use a visual layout:
  - Content describes a process (steps, flow) → process_flow
  - Content compares options → comparison_table
  - Content shows progress over time → timeline or roadmap
  - Content has metrics or KPIs → kpi_cards
  - Content describes a system → architecture
  - Content lists 2 categories → two_column_cards
  - Content describes a strategy → pyramid
  Default to "bullet_list" ONLY when truly no visual is appropriate.

LAYOUT DIVERSITY: Vary layouts slide-by-slide. Never repeat same layout 3+ times consecutively.
Layout variety: cover, agenda, two_column, full_visual, bullet_list, comparison_table, timeline_visual, process_flow, kpi_dashboard, section_divider, closing

Return ONLY valid JSON. No markdown. No explanations outside JSON.

{
  "analysis": {
    "presentation_type": "technical|executive|training|sales",
    "content_tone": "formal|conversational|technical|inspirational",
    "key_message": "single sentence audience must remember",
    "business_context": "brief context",
    "audience_needs": ["need1","need2","need3"],
    "recommended_sections": ["Section1","Section2"],
    "consultant_notes": "strategic advice for this presentation"
  },
  "structure": {
    "total_slides": number,
    "slide_plan": [
      {
        "slide_number": 1,
        "section": "Cover|Agenda|Executive Summary|Current State|Problem|Solution|Architecture|Process|Workflow|Features|Comparison|Benefits|KPI|Roadmap|Risks|Governance|Summary|Closing",
        "title": "exact slide title",
        "purpose": "why this slide exists",
        "layout": "cover|agenda|two_column|full_visual|bullet_list|comparison_table|timeline_visual|process_flow|kpi_dashboard|section_divider|closing",
        "visual_needed": true,
        "visual_type": "none|process_flow|architecture|flowchart|timeline|comparison_table|swot|kpi_cards|two_column_cards|pyramid|cycle|hierarchy|roadmap|agenda",
        "decision_reasoning": "why this layout+visual was chosen by the AI Decision Engine",
        "density_check": "full|partial — full=slide will use full content area"
      }
    ]
  }
}"""


def stage1_blueprint(config: dict) -> dict:
    duration       = config.get("duration", "15 Minutes")
    slide_range    = config.get("slide_range", "12-15")
    topic          = config.get("topic", "")
    objective      = config.get("objective", "")
    audience       = config.get("audience", "")
    presenter_type = config.get("presenter_type", "Technical Consultant")
    tech_level     = config.get("tech_level", "Intermediate")
    theme          = "Dark" if config.get("theme") == "dark" else "Light"
    content_depth  = config.get("content_depth", "Standard")
    visuals        = config.get("visuals", ["Automatically Decide"])
    sections       = config.get("sections", [])
    language       = config.get("language", "English")

    user_msg = f"""Run the AI Decision Engine and create the presentation blueprint:

TOPIC: {topic}
OBJECTIVE: {objective}
TARGET AUDIENCE: {audience}
PRESENTER: {presenter_type}
TECHNICAL LEVEL: {tech_level}
DURATION: {duration} — target {slide_range} slides total
CONTENT DEPTH: {content_depth}
THEME: {theme}
LANGUAGE: {language}
USER-REQUESTED SECTIONS: {', '.join(sections) if sections else 'NONE — use AI to decide intelligently based on topic'}
VISUAL PREFERENCES: {', '.join(visuals)}

MANDATORY REQUIREMENTS:
1. Slide 1 MUST be: layout=cover, slide_type=cover
2. Slide 2 MUST be: layout=agenda, visual_type=agenda
3. Last slide MUST be: layout=closing, section=Closing
4. For EACH slide: run the AI Decision Engine decision (is visual better than bullets?)
5. Use the exact right visual for the topic domain
6. Plan exactly {slide_range} slides — no more, no less
7. If user requested sections, include them; if not, INTELLIGENTLY select only sections that add value
8. Avoid generic slide titles like "Introduction" or "Overview" — use specific, topic-relevant titles
9. Mark density_check as "full" only when the slide will use the complete content area"""

    raw = _call_groq(STAGE1_SYSTEM, user_msg, max_tokens=3000)
    return json.loads(_clean_json(raw))


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2 — RICH CONTENT WITH FULL DENSITY
# ═══════════════════════════════════════════════════════════════════════════
STAGE2_SYSTEM = """You are an elite NTT DATA Senior Content Designer and PowerPoint Architect.
Generate COMPLETE, RICH slide content that fills every slide with consulting-grade material.

CONTENT DENSITY RULES (most important):
- Every content slide must have EITHER: 5+ bullets OR a full diagram with data
- Never produce a slide with only 2-3 bullets and no visual — that creates empty whitespace
- If a slide has 3-4 bullets, it MUST also have a visual element
- Bullets must be complete sentences (15-25 words each) with real insights
- Diagrams must have REAL data — actual component names, real phases, specific metrics

VISUAL QUALITY RULES:
- architecture: minimum 3 layers, each with 3-4 components using real technology names
- process_flow: minimum 4 steps with specific step descriptions (not vague labels)
- timeline: minimum 4 milestones with real deliverables per phase
- comparison_table: minimum 5 rows comparing meaningful attributes
- kpi_cards: minimum 4 cards with real percentages/numbers
- flowchart: minimum 6 nodes with proper start/decision/process/end shapes
- roadmap: minimum 3 phases with 3-4 specific tasks each

WORKFLOW QUALITY:
For flowcharts use these shapes: oval (start/end), diamond (decision), rect (process), rounded (connector)
Always include a start node and end node in flowcharts.

ICONS IN CONTENT: Use relevant Unicode symbols in bullet text where appropriate:
\u2714 for completed/achieved items, \u25b6 for process steps, \u2699 for configuration/settings,
\u26a0 for risks/warnings, \u2605 for key highlights, \u2194 for integrations

SECTION INTELLIGENCE: No placeholder text. No "insert diagram here". Every element must be specific.

ARCHITECTURAL SEPARATION — YOUR ROLE:
You generate STRUCTURED SPECIFICATIONS only. The Python renderer handles all visual positioning.
You specify WHAT to show (labels, values, connections, hierarchy). Python determines HOW to render it.
Never embed coordinate hints, pixel values, or manual positioning instructions in your output.
The renderer automatically handles: object sizing, proportional spacing, alignment, visual hierarchy.

Return ONLY valid JSON. No markdown. No text outside JSON.

{
  "presentation_title": "string",
  "theme": "light|dark",
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "cover|content|visual_full|closing",
      "layout": "cover|agenda|two_column|full_visual|bullet_list|comparison_table|timeline_visual|process_flow|kpi_dashboard|section_divider|closing",
      "title": "string",
      "subtitle": "string or null",
      "bullets": ["complete sentence 1 (15-25 words)","complete sentence 2"],
      "visual": {
        "type": "none|process_flow|architecture|flowchart|timeline|comparison_table|swot|kpi_cards|two_column_cards|pyramid|cycle|hierarchy|roadmap|agenda",
        "data": {}
      },
      "section": "SHORT_TAG|null",
      "speaker_notes": "string or null"
    }
  ]
}

VISUAL DATA SCHEMAS (use REAL data, not placeholders):
process_flow: {"steps":[{"id":1,"label":"Step Name","description":"specific 10-word description","color":"blue|teal|mid|navy"}],"direction":"horizontal|vertical"}
architecture: {"layers":[{"name":"Layer Name","color":"blue|teal|dark","components":[{"name":"Real Component Name","type":"box|cylinder|cloud","description":"role in system"}]}],"connections":[{"from":"ComponentA","to":"ComponentB","label":"protocol/method"}]}
flowchart: {"nodes":[{"id":"start","label":"Start","shape":"oval","color":"green"},{"id":"n1","label":"Process Step","shape":"rect","color":"blue"},{"id":"d1","label":"Decision?","shape":"diamond","color":"teal"},{"id":"end","label":"End","shape":"oval","color":"navy"}],"edges":[{"from":"start","to":"n1","label":""},{"from":"n1","to":"d1","label":""},{"from":"d1","to":"end","label":"Yes"},{"from":"d1","to":"n1","label":"No"}]}
timeline: {"milestones":[{"phase":"Phase Name","period":"Q1 2024","deliverables":["Specific deliverable 1","Specific deliverable 2","Specific deliverable 3"],"status":"done|active|planned"}]}
comparison_table: {"headers":["Aspect","Current State","Target State"],"rows":[{"aspect":"Specific attribute","values":["Current value","Target value"]}],"highlight_col":2}
swot: {"strengths":["Specific strength 1","Specific strength 2","Specific strength 3"],"weaknesses":["W1","W2"],"opportunities":["O1","O2"],"threats":["T1","T2"]}
kpi_cards: {"cards":[{"title":"Specific Metric","value":"85%","label":"improvement area","color":"blue|teal|green|accent","trend":"up|down|null","description":"1 short sentence explanation of this metric"}]}
agenda: {"items":[{"title":"Agenda Item Title","subtitle":"Brief specific description"}]}
two_column_cards: {"left_title":"Category A","right_title":"Category B","left_items":[{"icon":"\u25b6","title":"Item Title","body":"Specific description 10+ words"}],"right_items":[{"icon":"\u25b6","title":"Item Title","body":"Specific description"}]}
pyramid: {"levels":[{"label":"Top Level","description":"what this level means","color":"accent|blue|teal"}]}
cycle: {"steps":[{"label":"Phase Name","description":"specific description","color":"blue|teal|mid"}],"center_label":"Core Process"}
hierarchy: {"root":"Root Node","nodes":[{"label":"Child Node","color":"blue|teal|mid"}]}
roadmap: {"phases":[{"name":"Phase Name","period":"Q1-Q2 2024","tasks":["Specific Task 1","Specific Task 2","Specific Task 3"]}]}"""


def stage2_content(blueprint: dict, config: dict) -> dict:
    topic         = config.get("topic", "")
    audience      = config.get("audience", "")
    tech_level    = config.get("tech_level", "Intermediate")
    theme         = config.get("theme", "light")
    language      = config.get("language", "English")
    speaker_notes = config.get("speaker_notes", False)
    analysis      = blueprint.get("analysis", {})
    slide_plan    = blueprint.get("structure", {}).get("slide_plan", [])

    user_msg = f"""Generate COMPLETE, RICH slide content for this NTT DATA presentation.

TOPIC: {topic}
AUDIENCE: {audience} ({tech_level} level)
THEME: {"dark" if theme == "dark" else "light"}
LANGUAGE: {language}
SPEAKER NOTES: {"Generate detailed notes (3-5 sentences per slide)" if speaker_notes else "null for all"}

CONTEXT:
- Type: {analysis.get("presentation_type","professional")}
- Tone: {analysis.get("content_tone","formal")}
- Key message: {analysis.get("key_message","")}
- Recommended sections: {", ".join(analysis.get("recommended_sections", []))}
- Consultant notes: {analysis.get("consultant_notes","")}

BLUEPRINT TO EXECUTE:
{json.dumps(slide_plan, indent=2)}

DENSITY REQUIREMENTS (fill every slide):
1. COVER: title + subtitle + 2-3 metadata items (presenter, date, version) in bullets
2. AGENDA: agenda visual with ALL sections listed — no other content
3. EXECUTIVE SUMMARY: 5 bullets (Objective, Scope, Approach, Expected Outcome, Business Value) + kpi_cards visual
4. ARCHITECTURE slides: full architecture visual with 3+ layers and 3+ components each
5. PROCESS slides: process_flow with 4-6 steps, each step with specific description
6. FEATURES slides: two_column_cards with 4-5 items per side
7. BENEFITS slides: kpi_cards with 4 metrics + 3-4 supporting bullets
8. ROADMAP slides: timeline or roadmap visual with 4+ phases
9. CLOSING: just "Thank You", "Questions & Discussion", contact info if available
10. LANGUAGE: ALL text in {language}
11. ZERO PLACEHOLDER TEXT — every component name must be domain-specific
12. Make it indistinguishable from consultant-crafted work
13. KPI cards MUST include description (1-sentence explanation per card) and trend (up/down)
14. VISUAL FIRST: if a slide has 1-4 bullets, it MUST also include a visual element to fill the space
15. TYPOGRAPHY: title=30pt bold, bullets=12-13pt, captions=9-10pt — never oversized
16. SLIDE VALIDATION: before each slide, verify it has balanced whitespace — if not, add more content

VISUAL DECISION for each slide: ask "is a diagram better?" — if yes, provide FULL diagram data.
If bullets AND visual both exist on same slide, ensure visual is RICHER than the bullets alone."""

    raw = _call_groq(STAGE2_SYSTEM, user_msg, max_tokens=7000)
    return json.loads(_clean_json(raw))


def generate_presentation_plan(config: dict) -> dict:
    """Two-stage pipeline: AI Decision Engine → full slide plan."""
    blueprint  = stage1_blueprint(config)
    slide_plan = stage2_content(blueprint, config)
    slide_plan["_analysis"] = blueprint.get("analysis", {})
    return slide_plan
