"""
app/main.py

Full pipeline — all spec requirements wired together
─────────────────────────────────────────────────────
Req 1  — Multi-stage pipeline (intent → design → schema → validate → repair)
Req 2  — Strict schema enforcement (Pydantic + JSON serialization check)
Req 3  — Validation + repair engine (targeted, not blind retry)
Req 4  — Deterministic behaviour (temperature=0, structured prompts)
Req 5  — Execution awareness (executor produces migration plan + API manifest)
Req 6  — Failure handling (clarify stage documents assumptions + conflicts)
Req 8  — Cost/quality tradeoff (latency, retry count, quality score tracked)
"""

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline.intent import extract_intent
from pipeline.clarify import clarify_intent          # Req 6
from pipeline.design import design_system
from pipeline.schema import generate_schema
from pipeline.Validate import validate_schema
from pipeline.repair import repair_schema
from runtime.executor import execute_schema          # Req 5


# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Compylr AI",
    description="Compiler-style AI platform: natural language → validated, executable application schema",
    version="1.0.0"
)

# CORS — required for the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your Vercel URL before final deploy
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request model ─────────────────────────────────────────────────────────────

class CompileRequest(BaseModel):
    prompt: str


# ── Main compile endpoint ─────────────────────────────────────────────────────

@app.post("/compile")
def compile_app(request: CompileRequest):
    """
    Full compiler pipeline. Returns every stage's output plus:
    - clarification report (assumptions, conflicts, ambiguities)
    - execution report (migration plan, API manifest, permission matrix)
    - meta (latency per stage, total latency, retry count)
    """
    pipeline_start = time.time()
    stage_timings: dict = {}
    retry_count = 0

    # ── Stage 1: Intent Extraction ────────────────────────────────────────────
    t = time.time()
    intent = extract_intent(request.prompt)
    stage_timings["intent_ms"] = round((time.time() - t) * 1000, 1)

    if not intent:
        raise HTTPException(status_code=500, detail="Intent extraction failed.")

    # ── Stage 2: Clarification / Failure Handling (Req 6) ─────────────────────
    # Always runs. Never blocks — documents assumptions instead.
    t = time.time()
    clarification = clarify_intent(intent, request.prompt)
    stage_timings["clarify_ms"] = round((time.time() - t) * 1000, 1)

    print(f"\n📋 Clarity score: {clarification.clarity_score}/10 "
          f"| Conflicts: {len(clarification.conflicts)} "
          f"| Assumptions: {len(clarification.assumptions)}")

    # ── Stage 3: System Design ────────────────────────────────────────────────
    t = time.time()
    design = design_system(intent)
    stage_timings["design_ms"] = round((time.time() - t) * 1000, 1)

    if not design:
        raise HTTPException(status_code=500, detail="System design failed.")

    # ── Stage 4: Schema Generation ────────────────────────────────────────────
    t = time.time()
    schema = generate_schema(design)
    stage_timings["schema_ms"] = round((time.time() - t) * 1000, 1)

    if not schema:
        raise HTTPException(status_code=500, detail="Schema generation failed.")

    # ── Stage 5: Validation ───────────────────────────────────────────────────
    t = time.time()
    validation = validate_schema(schema)
    stage_timings["validation_ms"] = round((time.time() - t) * 1000, 1)

    # ── Stage 6: Repair (only if validation failed) ───────────────────────────
    # Targeted repair — not blind full retry (spec req 3 core requirement)
    repair_timings = []
    if not validation.is_valid:
        for attempt in range(1, 4):          # max 3 targeted repair cycles
            t = time.time()
            schema = repair_schema(schema, validation)
            validation = validate_schema(schema)
            repair_timings.append(round((time.time() - t) * 1000, 1))
            retry_count += 1
            if validation.is_valid:
                break

    stage_timings["repair_attempts"] = retry_count
    stage_timings["repair_ms_per_attempt"] = repair_timings

    # ── Stage 7: Execution (Req 5) ────────────────────────────────────────────
    total_latency_ms = round((time.time() - pipeline_start) * 1000, 1)

    t = time.time()
    execution_report = execute_schema(
        schema,
        latency_ms=total_latency_ms,
        retry_count=retry_count
    )
    stage_timings["executor_ms"] = round((time.time() - t) * 1000, 1)

    # ── Final response ────────────────────────────────────────────────────────
    return {
        # Stage outputs
        "intent": intent,

        "clarification": {                              # Req 6
            "clarity_score":         clarification.clarity_score,
            "is_clear":              clarification.is_clear,
            "ambiguities":           clarification.ambiguities,
            "conflicts":             clarification.conflicts,
            "assumptions":           clarification.assumptions,
            "clarifying_questions":  clarification.clarifying_questions,
        },

        "design": design.model_dump(),

        "schema": schema.model_dump(),

        "validation": {
            "passed": validation.is_valid,
            "errors": validation.errors,
        },

        "execution": execution_report,                  # Req 5

        # Pipeline metadata (Req 8 — cost/quality traceability)
        "meta": {
            "total_latency_ms": total_latency_ms,
            "stage_timings":    stage_timings,
            "retry_count":      retry_count,
            "prompt_length":    len(request.prompt),
        }
    }


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "service": "Compylr AI",
        "status":  "running",
        "version": "1.0.0",
        "pipeline_stages": [
            "intent_extraction",
            "clarification",
            "system_design",
            "schema_generation",
            "validation",
            "repair",
            "execution"
        ]
    }