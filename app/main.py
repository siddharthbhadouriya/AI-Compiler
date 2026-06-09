from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pipeline.intent import extract_intent
from pipeline.design import design_system
from pipeline.schema import generate_schema
from pipeline.Validate import validate_schema
from pipeline.repair import repair_schema


class CompileRequest(BaseModel):
    prompt: str


app = FastAPI()


@app.post("/compile")
def compile_app(request: CompileRequest):
    # ── Stage 1: Intent Extraction ──────────────────────────────
    intent = extract_intent(request.prompt)
    if not intent:
        raise HTTPException(status_code=500, detail="Intent extraction failed.")

    # ── Stage 2: System Design ──────────────────────────────────
    design = design_system(intent)
    if not design:
        raise HTTPException(status_code=500, detail="System design failed.")

    # ── Stage 3: Schema Generation ──────────────────────────────
    schema = generate_schema(design)
    if not schema:
        raise HTTPException(status_code=500, detail="Schema generation failed.")

    # ── Stage 4: Validation ─────────────────────────────────────
    validation = validate_schema(schema)

    # ── Stage 5: Repair (only if validation failed) ─────────────
    if not validation.is_valid:
        schema = repair_schema(schema, validation)
        validation = validate_schema(schema)  # final check after repair

    return {
        "intent": intent,
        "design": design.model_dump(),
        "schema": schema.model_dump(),
        "validation": {
            "passed": validation.is_valid,
            "errors": validation.errors
        }
    }


@app.get("/")
def home():
    return {"message": "Compylr AI — server is running"}