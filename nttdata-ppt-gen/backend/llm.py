"""
NTT DATA AI Presentation Generator — Two-Stage Groq Pipeline v2
Implements: AI Decision Engine, Visual Intelligence, Section Selection, Content Density.
"""
import os, json, re
from groq import Groq

_client = None

def get_client(api_key: str = None):
    global _client
    if api_key:
        return Groq(api_key=api_key)
    if _client is None:
        key = os.getenv("GROQ_API_KEY", "")
        if not key or key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=key)
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

def _call_groq(system: str, user: str, max_tokens: int = 7000,
               model_override: str = None, use_secondary: bool = False) -> str:
    if use_secondary:
        key = os.getenv("GROQ_API_KEY_2", "")
        if not key:
            key = os.getenv("GROQ_API_KEY", "")
        client = Groq(api_key=key)
    else:
        client = get_client()
    model = model_override or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    resp  = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.1,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════════════════════
# # ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 — BLUEPRINT WITH AI DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════════════
STAGE1_SYSTEM = """You are an elite NTT DATA Senior Presentation Architect with 15 years of consulting experience.

STEP 0 — COLLECT PRESENTER METADATA FIRST:
Before planning any slides, confirm these values are available in the config.
Use them exactly as provided. NEVER output bracket placeholders like [Your Name], [Current Date], [Your Email].
If a value is missing from config, use these safe defaults:
  presenter_name → "NTT DATA Consultant"
  date           → "2026"
  version        → "1.0"
  contact_email  → omit entirely (do not show a blank or placeholder)

STATISTICS INTEGRITY RULES (non-negotiable):
1. NEVER invent percentage metrics, benchmark figures, or ROI numbers without a real source.
2. Acceptable sources: Gartner, McKinsey, IDC, vendor documentation, academic benchmarks, NTT DATA case study data.
3. If no verifiable stat exists for a KPI slide on this topic, plan a comparison_table or two_column_cards layout instead.
4. A slide with 0 KPI cards is better than a slide with fabricated KPI cards.
Examples of ALLOWED stats for Neural Networks:
  - ImageNet top-5 accuracy >98% (ResNet benchmark)
  - GPT-4 MMLU score 86.4% (OpenAI 2023)
  - Transformer training efficiency vs RNN: 3-5x faster convergence
Examples of FORBIDDEN stats (fabricated, no source):
  - "95% Accuracy improvement area"
  - "80% Flexibility scope"
  - Any round number with no source or domain basis

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
- Business health, metrics, outcomes → kpi_cards (only with real sourced stats)
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

SECTION LABEL RULES (the "section" field must match slide content — not a random template label):
- A slide introducing concepts/fundamentals → FUNDAMENTALS or INTRODUCTION
- A slide showing architecture/system design → ARCHITECTURE
- A slide listing features or components → FEATURES
- A slide showing benefits, advantages → BENEFITS
- A slide with KPI metrics → METRICS
- A slide summarizing at the END of the deck → SUMMARY or KEY_TAKEAWAYS
- EXECUTIVE_SUMMARY must ONLY appear in slides 2-4, as a high-level preview of the whole presentation
- PROPOSED_SOLUTION must ONLY appear on slides that describe a proposed solution to a stated problem
- NEVER assign a section label from a different content category than the slide's actual content
- Wrong: slide about neural network layers labeled "PROPOSED_SOLUTION"
- Wrong: final recap slide labeled "EXECUTIVE_SUMMARY"
- Right: slide about network layers labeled "FUNDAMENTALS"
- Right: final recap slide labeled "KEY_TAKEAWAYS"

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
  "presenter_meta": {
    "presenter_name": "value from config or NTT DATA Consultant",
    "date": "value from config or 2026",
    "version": "value from config or 1.0",
    "contact_email": "value from config or null — never a placeholder string"
  },
  "structure": {
    "total_slides": number,
    "slide_plan": [
      {
        "slide_number": 1,
        "section": "FUNDAMENTALS|INTRODUCTION|ARCHITECTURE|FEATURES|BENEFITS|METRICS|SUMMARY|KEY_TAKEAWAYS|EXECUTIVE_SUMMARY|PROPOSED_SOLUTION|CLOSING|AGENDA|COVER — must semantically match slide content",
        "title": "exact slide title — specific, never generic like Introduction or Overview",
        "purpose": "why this slide exists",
        "layout": "cover|agenda|two_column|full_visual|bullet_list|comparison_table|timeline_visual|process_flow|kpi_dashboard|section_divider|closing",
        "visual_needed": true,
        "visual_type": "none|process_flow|architecture|flowchart|timeline|comparison_table|swot|kpi_cards|two_column_cards|pyramid|cycle|hierarchy|roadmap|agenda",
        "decision_reasoning": "why this layout+visual was chosen by the AI Decision Engine",
        "density_check": "full|partial — full=slide will use full content area",
        "stats_required": false
      }
    ]
  }
}"""


def stage1_blueprint(config: dict) -> dict:
    duration      = config.get("duration", "15 Minutes")
    slide_range   = config.get("slide_range", "12-15")
    topic         = config.get("topic", "")
    objective     = config.get("objective", "")
    audience      = config.get("audience", "")
    tech_level    = config.get("tech_level", "Intermediate")
    theme         = "Dark" if config.get("theme") == "dark" else "Light"
    content_depth = config.get("content_depth", "Standard")
    visuals       = config.get("visuals", ["Automatically Decide"])
    language      = config.get("language", "English")

    user_msg = f"""Run the AI Decision Engine and create the presentation blueprint:

TOPIC: {topic}
OBJECTIVE (this defines the PURPOSE and TONE — read this carefully): {objective}
TARGET AUDIENCE: {audience}
TECHNICAL LEVEL: {tech_level}
DURATION: {duration} — target {slide_range} slides total
CONTENT DEPTH: {content_depth}
THEME: {theme}
LANGUAGE: {language}
USER-REQUESTED SECTIONS: NONE — AI must intelligently select sections based on topic, objective, audience and duration only.
VISUAL PREFERENCES: {', '.join(visuals)}
PRESENTER NAME: {config.get('presenter_name', 'NTT DATA Consultant')}
DATE: {config.get('date', '2026')}
VERSION: {config.get('version', '1.0')}
CONTACT EMAIL: {config.get('contact_email', 'omit')}

OBJECTIVE ANALYSIS — before planning any slides, analyse the objective:
- If objective is "Project Update" → slides must show current status, 
  progress, blockers, next steps. NOT a general introduction.
- If objective is "Executive Overview" → slides must be high-level, 
  business-focused, no deep technical detail.
- If objective is "Technical Deep Dive" → slides must include 
  architecture, code examples, implementation details.
- If objective is "Client Proposal" → slides must show business value, 
  ROI, implementation approach.
- If objective is "Training Session" → slides must be educational, 
  step-by-step, with examples.
- If objective is "Business Case" → slides must show problem, solution, 
  cost-benefit, ROI.
- The objective OVERRIDES generic topic structure. A "Project Update" 
  on Neural Networks is NOT the same as "Inform/Educate" on Neural Networks.
- Every slide title and section must reflect the objective, not just the topic.

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

    raw = _call_groq(STAGE1_SYSTEM, user_msg, max_tokens=4000)
    return json.loads(_clean_json(raw))


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2 — RICH CONTENT WITH FULL DENSITY
# ═══════════════════════════════════════════════════════════════════════════
STAGE2_SYSTEM = """You are an elite NTT DATA Senior Content Designer and PowerPoint Architect.
Generate COMPLETE, RICH slide content that fills every slide with consulting-grade material.

METADATA RULES (apply to every generation):
- Cover slide MUST show real values for Presenter, Date, Version — taken from presenter_meta in the blueprint
- NEVER output bracket placeholders: [Your Name], [Current Date], [Your Email], [Insert here]
- If contact_email is null in presenter_meta, omit the contact line from the closing slide entirely
- If any metadata value is missing, use the safe default, not a placeholder

STATISTICS INTEGRITY (non-negotiable):
- NEVER invent percentage figures, benchmark scores, or ROI numbers
- Every number in a kpi_cards visual MUST have a real source field populated
- If you cannot provide a real source for a stat, do NOT include that card
- Replace an unsourceable kpi_cards visual with comparison_table or two_column_cards instead
- Fabricated statistics (e.g. "95% accuracy improvement area") are worse than no statistics at all

CONTENT DENSITY RULES (most important):
- Every content slide must have EITHER: 5+ bullets OR a full diagram with data
- Never produce a slide with only 2-3 bullets and no visual — that creates empty whitespace
- If a slide has 3-4 bullets, it MUST also have a visual element
- Bullets must pass the quality standard below — no surface-level one-liners

BULLET QUALITY STANDARD — every bullet must answer all three:
  (1) WHAT: the specific concept, component, or fact
  (2) WHY IT MATTERS: business or technical significance
  (3) CONTEXT: one real-world example, metric, or application

  REJECTED bullet (fails standard — too vague, no insight):
    "Neural networks can learn from complex data"

  ACCEPTED bullet (passes standard):
    "Neural networks learn hierarchical feature representations directly from raw data,
     eliminating months of manual feature engineering previously required for image
     recognition and NLP tasks — enabling faster model iteration cycles."

  Minimum bullet density per slide:
    - 5+ bullets → may stand alone without a visual
    - 3-4 bullets → MUST be paired with a visual element
    - 1-2 bullets → FORBIDDEN as standalone — always pair with a rich visual

VISUAL QUALITY RULES:
- architecture: minimum 3 layers, each with 3-4 components using real technology names; connections array must be populated — every component must connect to at least one other
- process_flow: minimum 5 steps, maximum 6 steps — more steps = less empty space below the diagram; each step needs a specific 8-12 word description
- timeline: minimum 4 milestones, ideally 5 — more milestones fill the horizontal space better; each milestone needs 3 deliverables minimum
- comparison_table: minimum 5 rows comparing meaningful attributes
- kpi_cards: always use exactly 4 cards — never 3, never 5. 4 cards fills the width perfectly with no gaps
- flowchart: minimum 6 nodes; every node except start/end must have both an incoming and outgoing edge; no orphan nodes
- roadmap: minimum 4 phases with 4 specific tasks each — more phases and tasks fill the slide area completely

DIAGRAM COMPLETENESS RULES:
- architecture: ALL components must appear in at least one entry in the connections array
- flowchart: no disconnected nodes — every node except start/end needs in AND out edges
- Neural network / AI pipeline diagrams: show connections between ALL layers; each node in layer N connects to nodes in layer N+1; label each connection with signal type or data flow
- hierarchy: root connects to all top-level children; no orphan nodes allowed
- process_flow: continuous chain only — step N must connect to step N+1; no isolated steps

SECTION LABEL VALIDATION (check before writing each slide's section field):
- Fundamentals/intro content → FUNDAMENTALS or INTRODUCTION
- Architecture/system design → ARCHITECTURE
- Features/components listing → FEATURES
- Benefits/advantages → BENEFITS
- KPI metrics → METRICS
- Final recap at end of deck → SUMMARY or KEY_TAKEAWAYS
- EXECUTIVE_SUMMARY → ONLY for slides 2-4 that preview the full presentation
- PROPOSED_SOLUTION → ONLY when the slide explicitly describes a proposed solution to a stated problem
- NEVER assign a section label from a different content category than what the slide actually contains

WORKFLOW QUALITY:
For flowcharts use these shapes: oval (start/end), diamond (decision), rect (process), rounded (connector)
Always include a start node and end node in flowcharts.

ICONS IN CONTENT: Use relevant Unicode symbols in bullet text where appropriate:
\u2714 for completed/achieved items, \u25b6 for process steps, \u2699 for configuration/settings,
\u26a0 for risks/warnings, \u2605 for key highlights, \u2194 for integrations

SECTION INTELLIGENCE: No placeholder text. No "insert diagram here". Every element must be specific.

LAYOUT VARIETY RULES (enforced):
- NEVER use architecture visual on two consecutive slides
- NEVER use process_flow visual on two consecutive slides  
- For a 9-slide Technical Deep Dive, use AT LEAST 4 different visual types
- Required variety: must include comparison_table OR flowchart OR roadmap in every deck
- If slide N uses architecture, slide N+1 must use a different visual type
- Suggested variety pattern: architecture → two_column_cards → process_flow → comparison_table → timeline

CONTENT COMPLETENESS (absolute rules — not suggestions):
- Architecture MUST have minimum 3 components per layer — ALWAYS
- Use real technology names: Conv2D, MaxPool2D, ReLU, Dense, Dropout, BatchNorm
- NEVER output an architecture layer with only 1 or 2 components
- Every content slide with a visual MUST also have minimum 3 bullets
- Bullets explain WHAT the visual shows, WHY it matters, HOW it works
- A slide with only a diagram and no bullets is INCOMPLETE and FORBIDDEN

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
      "bullets": ["complete sentence 1 (passes quality standard)","complete sentence 2"],
      "visual": {
        "type": "none|process_flow|architecture|flowchart|timeline|comparison_table|swot|kpi_cards|two_column_cards|pyramid|cycle|hierarchy|roadmap|agenda",
        "data": {}
      },
      "section": "SHORT_TAG matching slide content — see section label rules above",
      "speaker_notes": "string or null"
    }
  ]
}

VISUAL DATA SCHEMAS (use REAL data, not placeholders):
process_flow: {"steps":[{"id":1,"label":"Step Name","description":"specific 10-word description","color":"blue|teal|mid|navy"}],"direction":"horizontal|vertical","insight":"one key takeaway sentence about this process — shown as a highlight bar below the diagram"}
architecture: {"layers":[{"name":"Layer Name","color":"blue|teal|dark","components":[{"name":"Real Component Name","type":"box|cylinder|cloud","description":"role in system"}]}],"connections":[{"from":"ComponentA","to":"ComponentB","label":"protocol/method"}]}
flowchart: {"nodes":[{"id":"start","label":"Start","shape":"oval","color":"green"},{"id":"n1","label":"Process Step","shape":"rect","color":"blue"},{"id":"d1","label":"Decision?","shape":"diamond","color":"teal"},{"id":"end","label":"End","shape":"oval","color":"navy"}],"edges":[{"from":"start","to":"n1","label":""},{"from":"n1","to":"d1","label":""},{"from":"d1","to":"end","label":"Yes"},{"from":"d1","to":"n1","label":"No"}]}
timeline: {"milestones":[{"phase":"Phase Name","period":"Q1 2024","deliverables":["Specific deliverable 1","Specific deliverable 2","Specific deliverable 3"],"status":"done|active|planned"}],"summary":"one sentence summarising the overall timeline goal — shown as highlight bar below"}
comparison_table: {"headers":["Aspect","Current State","Target State"],"rows":[{"aspect":"Specific attribute","values":["Current value","Target value"]}],"highlight_col":2}
swot: {"strengths":["Specific strength 1","Specific strength 2","Specific strength 3"],"weaknesses":["W1","W2"],"opportunities":["O1","O2"],"threats":["T1","T2"]}
kpi_cards: {"cards":[{"title":"Specific Metric Name","value":"86.4%","label":"exact context e.g. GPT-4 MMLU benchmark score","color":"blue|teal|green|accent","trend":"up|down|null","description":"1 sentence explaining what this number means in practice","source":"OpenAI Technical Report 2023 | Gartner 2024 | McKinsey AI Report | NTT DATA case study"}]}
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
13. KPI cards MUST include description (1-sentence explanation per card), trend (up/down), and source (real reference)
14. VISUAL FIRST: if a slide has 1-4 bullets, it MUST also include a visual element to fill the space
15. TYPOGRAPHY: title=30pt bold, bullets=12-13pt, captions=9-10pt — never oversized
16. SLIDE VALIDATION: before each slide, verify it has balanced whitespace — if not, add more content

METADATA TO USE ON COVER SLIDE:
  Presenter: {config.get('presenter_name', 'NTT DATA Consultant')}
  Date: {config.get('date', '2026')}
  Version: {config.get('version', '1.0')}
  Email: {config.get('contact_email', '') or 'omit — do not show placeholder'}
Use these exact values. NEVER output bracket placeholders like [Your Name].

SECTION LABEL VALIDATION: before writing each slide's section field, verify it matches the content.
A fundamentals slide → FUNDAMENTALS. A final recap → SUMMARY or KEY_TAKEAWAYS, not EXECUTIVE_SUMMARY.

VISUAL DECISION for each slide: ask "is a diagram better?" — if yes, provide FULL diagram data.
If bullets AND visual both exist on same slide, ensure visual is RICHER than the bullets alone."""

    raw = _call_groq(STAGE2_SYSTEM, user_msg, max_tokens=7500,
                     use_secondary=True)
    return json.loads(_clean_json(raw))
  


def validate_and_fix(slide_plan: dict) -> dict:
    for slide in slide_plan.get("slides", []):
        visual      = slide.get("visual", {})
        section     = (slide.get("section") or "").upper()
        title       = (slide.get("title")   or "").lower()
        slide_num   = slide.get("slide_number", 0)

        # Fix 1 — remove KPI cards with no source field
        if visual.get("type") == "kpi_cards":
            cards = visual.get("data", {}).get("cards", [])
            good  = [c for c in cards
                     if str(c.get("source") or "").strip()
                     and str(c.get("source") or "").strip().lower() != "null"]
            if not good:
                visual["type"] = "two_column_cards"
                visual["data"] = {}
            else:
                visual["data"]["cards"] = good

        # Fix 2 — PROPOSED_SOLUTION only allowed when title contains
        # solution-related words
        if section == "PROPOSED_SOLUTION":
            keywords = {"solution", "proposal", "recommend", "approach"}
            if not any(k in title for k in keywords):
                slide["section"] = "FEATURES"

        # Fix 3 — EXECUTIVE_SUMMARY only allowed on slides 2-4
        if section == "EXECUTIVE_SUMMARY" and slide_num > 4:
            slide["section"] = "SUMMARY"

    # Fix 4 — remove duplicate visuals across slides
    seen_visuals = {}
    for slide in slide_plan.get("slides", []):
        visual = slide.get("visual", {})
        vtype  = visual.get("type", "none")
        if vtype in ("none", None):
            continue
        data = visual.get("data", {})
        # For kpi_cards, fingerprint using sorted values only
        if vtype == "kpi_cards":
            values = sorted([
                c.get("value","") for c in data.get("cards", [])
            ])
            fingerprint = vtype + str(values)
        else:
            fingerprint = json.dumps(data, sort_keys=True)
        if fingerprint in seen_visuals:
            slide["visual"] = {"type": "none", "data": {}}
        else:
            seen_visuals[fingerprint] = slide.get("slide_number")

    # Fix 5 — architecture: ensure minimum 3 components per layer
    for slide in slide_plan.get("slides", []):
        visual = slide.get("visual", {})
        if visual.get("type") == "architecture":
            layers = visual.get("data", {}).get("layers", [])
            for layer in layers:
                comps = layer.get("components", [])
                if len(comps) < 3:
                    base = comps[0] if comps else {"name": layer.get("name","Component"), "type": "box", "description": "Core component"}
                    while len(layer["components"]) < 3:
                        idx = len(layer["components"]) + 1
                        layer["components"].append({
                            "name": f"{base.get('name','')} {idx}",
                            "type": base.get("type", "box"),
                            "description": f"Supporting {base.get('description','component')}"
                        })

    # Fix 6 — prevent consecutive slides with same visual type
    slides = slide_plan.get("slides", [])
    for i in range(1, len(slides)):
        prev = slides[i-1].get("visual", {}).get("type", "none")
        curr = slides[i].get("visual",  {}).get("type", "none")
        if prev == curr == "architecture":
            # Second consecutive architecture — convert to two_column_cards
            curr_slide = slides[i]
            layers = curr_slide.get("visual", {}).get("data", {}).get("layers", [])
            items = []
            for layer in layers:
                for comp in layer.get("components", []):
                    items.append({
                        "icon": "▶",
                        "title": comp.get("name", ""),
                        "body": comp.get("description", "")
                    })
            half = len(items) // 2
            curr_slide["visual"] = {
                "type": "two_column_cards",
                "data": {
                    "left_title": "Key Components",
                    "right_title": "Functions",
                    "left_items": items[:half],
                    "right_items": items[half:]
                }
            }
            curr_slide["layout"] = "two_column"

    return slide_plan


def debug_schema_check(slide_plan: dict) -> None:
    issues = []
    for slide in slide_plan.get("slides", []):
        n = slide.get("slide_number")
        
        # Check bullets quality
        bullets = slide.get("bullets") or []
        short = [b for b in bullets if len(b.split()) < 10]
        if short:
            issues.append(f"Slide {n}: {len(short)} bullet(s) under 10 words")
        
        # Check KPI cards have source
        visual = slide.get("visual", {})
        if visual.get("type") == "kpi_cards":
            cards = visual.get("data", {}).get("cards", [])
            for i, c in enumerate(cards):
                if not str(c.get("source") or "").strip():
                    issues.append(f"Slide {n}: KPI card {i+1} '{c.get('title')}' has no source")
                if not c.get("value"):
                    issues.append(f"Slide {n}: KPI card {i+1} has no value")
        
        # Check section label
        section = (slide.get("section") or "").upper()
        title   = (slide.get("title")   or "").lower()
        num     = slide.get("slide_number", 0)
        if section == "PROPOSED_SOLUTION":
            if not any(k in title for k in ["solution","proposal","recommend"]):
                issues.append(f"Slide {n}: PROPOSED_SOLUTION label but title is '{slide.get('title')}'")
        if section == "EXECUTIVE_SUMMARY" and num > 4:
            issues.append(f"Slide {n}: EXECUTIVE_SUMMARY used on slide {num} (should be 2-4 only)")
        
        # Check visual completeness
        if visual.get("type") == "architecture":
            connections = visual.get("data", {}).get("connections", [])
            if not connections:
                issues.append(f"Slide {n}: architecture has no connections array")
        
        if visual.get("type") == "two_column_cards":
            left  = visual.get("data", {}).get("left_items",  [])
            right = visual.get("data", {}).get("right_items", [])
            if not left:
                issues.append(f"Slide {n}: two_column_cards left column is empty")
            if not right:
                issues.append(f"Slide {n}: two_column_cards right column is empty")

    if issues:
        print("\n===== SCHEMA VALIDATION ISSUES =====")
        for issue in issues:
            print(f"  ⚠  {issue}")
        print(f"  Total: {len(issues)} issue(s)")
        print("=====================================\n")
    else:
        print("\n  ✓ Schema validation passed — no issues found\n")


def debug_render_check(slide_plan: dict) -> None:
    issues = []
    for slide in slide_plan.get("slides", []):
        n      = slide.get("slide_number")
        layout = (slide.get("layout") or "").lower()
        visual = slide.get("visual", {})
        vtype  = visual.get("type", "none")
        vdata  = visual.get("data", {})
        bullets = slide.get("bullets") or []

        # Check 1 — empty slide (nothing to render)
        has_bullets = len(bullets) > 0
        has_visual  = vtype not in ("none", None, "")
        if not has_bullets and not has_visual:
            issues.append(f"Slide {n}: completely empty — no bullets and no visual")

        # Check 2 — layout says two_column but visual data is empty
        if vtype == "two_column_cards":
            left  = vdata.get("left_items",  [])
            right = vdata.get("right_items", [])
            if not left and not right:
                issues.append(f"Slide {n}: two_column_cards has no items in either column — will render blank")
            elif not left:
                issues.append(f"Slide {n}: two_column_cards left column empty — will look unbalanced")
            elif not right:
                issues.append(f"Slide {n}: two_column_cards right column empty — will look unbalanced")

        # Check 3 — kpi_cards with no cards
        if vtype == "kpi_cards":
            cards = vdata.get("cards", [])
            if not cards:
                issues.append(f"Slide {n}: kpi_cards visual has 0 cards — will render blank")
            for i, c in enumerate(cards):
                if not c.get("value"):
                    issues.append(f"Slide {n}: KPI card {i+1} missing value field — will render blank number")
                if not c.get("title"):
                    issues.append(f"Slide {n}: KPI card {i+1} missing title — will render unnamed card")

        # Check 4 — process_flow with too few steps
        if vtype == "process_flow":
            steps = vdata.get("steps", [])
            if len(steps) < 3:
                issues.append(f"Slide {n}: process_flow has only {len(steps)} step(s) — will look sparse")
            for i, s in enumerate(steps):
                if not s.get("label"):
                    issues.append(f"Slide {n}: process_flow step {i+1} has no label")
                if not s.get("description"):
                    issues.append(f"Slide {n}: process_flow step {i+1} has no description — box will be empty")

        # Check 5 — architecture with no layers or empty components
        if vtype == "architecture":
            layers = vdata.get("layers", [])
            if not layers:
                issues.append(f"Slide {n}: architecture has no layers — will render blank")
            for i, layer in enumerate(layers):
                comps = layer.get("components", [])
                if not comps:
                    issues.append(f"Slide {n}: architecture layer '{layer.get('name')}' has no components")
                elif len(comps) < 2:
                    issues.append(f"Slide {n}: architecture layer '{layer.get('name')}' has only {len(comps)} component — minimum 2 required")
            connections = vdata.get("connections", [])
            if not connections:
                issues.append(f"Slide {n}: architecture has no connections — nodes will be unconnected boxes")

        # Check 6 — comparison_table with no rows
        if vtype == "comparison_table":
            rows = vdata.get("rows", [])
            if not rows:
                issues.append(f"Slide {n}: comparison_table has no rows — will render empty table")
            headers = vdata.get("headers", [])
            if not headers:
                issues.append(f"Slide {n}: comparison_table has no headers")

        # Check 7 — agenda with no items
        if vtype == "agenda":
            items = vdata.get("items", [])
            if not items:
                issues.append(f"Slide {n}: agenda has no items — will render blank")

        # Check 8 — timeline with no milestones
        if vtype == "timeline":
            milestones = vdata.get("milestones", [])
            if not milestones:
                issues.append(f"Slide {n}: timeline has no milestones — will render blank")
            for m in milestones:
                if not m.get("deliverables"):
                    issues.append(f"Slide {n}: timeline phase '{m.get('phase')}' has no deliverables")

        # Check 9 — roadmap with no phases
        if vtype == "roadmap":
            phases = vdata.get("phases", [])
            if not phases:
                issues.append(f"Slide {n}: roadmap has no phases — will render blank")
            for p in phases:
                if not p.get("tasks"):
                    issues.append(f"Slide {n}: roadmap phase '{p.get('name')}' has no tasks")

        # Check 10 — bullet + visual mismatch
        if len(bullets) > 0 and len(bullets) < 3 and not has_visual:
            issues.append(f"Slide {n}: only {len(bullets)} bullet(s) and no visual — will have large empty space")

        # Check 11 — title missing
        if not slide.get("title"):
            issues.append(f"Slide {n}: no title — slide header will be blank")

    if issues:
        print("\n===== RENDER CHECK ISSUES =====")
        for issue in issues:
            print(f"  ⚠  {issue}")
        print(f"  Total: {len(issues)} render issue(s) to fix")
        print("================================\n")
    else:
        print("\n  ✓ Render check passed — all slides have complete data\n")


def generate_presentation_plan(config: dict) -> dict:
    """Two-stage pipeline: AI Decision Engine → full slide plan."""
    blueprint  = stage1_blueprint(config)
    slide_plan = stage2_content(blueprint, config)
    slide_plan = validate_and_fix(slide_plan)

    # Slide count check
    duration = config.get("duration", "10 Minutes")
    min_slides_map = {
        "5 Minutes": 5, "10 Minutes": 8, "15 Minutes": 12,
        "20 Minutes": 15, "30 Minutes": 20, "45 Minutes": 28, "60 Minutes": 35
    }
    min_s = min_slides_map.get(duration, 8)
    actual_s = len(slide_plan.get("slides", []))
    if actual_s < min_s:
        print(f"\n  ⚠  WARNING: Only {actual_s} slides generated for {duration} (minimum {min_s})")
    else:
        print(f"\n  ✓ Slide count: {actual_s} slides for {duration}\n")

    debug_schema_check(slide_plan)
    debug_render_check(slide_plan)
    slide_plan["_analysis"] = blueprint.get("analysis", {})
    return slide_plan
