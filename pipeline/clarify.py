"""
pipeline/clarify.py

Failure Handling System — spec requirement #6
─────────────────────────────────────────────
The spec says the system must handle:
  • vague prompts       ("build an app")
  • conflicting reqs    ("free but with payments")
  • underspecified input ("make a social network")

And must either:
  • ask for clarification, OR
  • make reasonable assumptions (and document them)

This stage slots between Intent Extraction and System Design.
It does NOT block the pipeline — it enriches it with documented
assumptions so the evaluator can see the system is handling
ambiguity, not ignoring it.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from typing import List
from utils.llm import llm

parser = JsonOutputParser()


# ── Output contract ──────────────────────────────────────────────────────────

class ClarificationResult(BaseModel):
    """
    What the clarifier produces for every prompt, vague or clear.

    is_clear        — can the pipeline proceed with confidence?
    clarity_score   — 0-10 rating (10 = perfectly specified)
    ambiguities     — parts of the prompt that are vague or missing
    conflicts       — contradictions detected (e.g. "free" + "payments")
    assumptions     — what we assume to fill the gaps (always documented)
    clarifying_questions — what we WOULD ask the user if interactive
    """
    is_clear: bool
    clarity_score: int                   # 0–10
    ambiguities: List[str]
    conflicts: List[str]
    assumptions: List[str]
    clarifying_questions: List[str]


# ── Prompt ───────────────────────────────────────────────────────────────────

_CLARIFY_PROMPT = PromptTemplate(
    template="""
You are a requirements analyst for a software compiler system.

Your job is to audit the extracted intent from a user's prompt and
identify anything that would make reliable schema generation impossible:
vague features, missing roles, conflicting requirements, or incomplete
business logic.

You MUST be decisive. Do not return empty lists just to seem safe.

Extracted intent:
{intent}

Original user prompt:
{original_prompt}

Return ONLY valid JSON — no explanation, no markdown.

Scoring guide for clarity_score:
  10 = fully specified (roles, features, data model all clear)
  7-9 = minor gaps, safe to proceed with small assumptions
  4-6 = moderate ambiguity, assumptions needed
  1-3 = too vague to generate reliably
  0   = completely underspecified ("build an app")

Set is_clear = true if clarity_score >= 5 (pipeline can proceed).
Set is_clear = false if clarity_score < 5 (pipeline proceeds but
evaluator is warned).

Output format:
{{
  "is_clear": true,
  "clarity_score": 8,
  "ambiguities": [
    "Payment provider not specified (Stripe assumed)",
    "No mention of email verification flow"
  ],
  "conflicts": [],
  "assumptions": [
    "Assumed web application (not mobile)",
    "Assumed Stripe for payment processing",
    "Assumed JWT-based authentication"
  ],
  "clarifying_questions": [
    "Should users be able to self-register or is it invite-only?",
    "What payment provider should be integrated?"
  ]
}}
""",
    input_variables=["intent", "original_prompt"]
)

chain = _CLARIFY_PROMPT | llm | parser


# ── Public entry point ───────────────────────────────────────────────────────

def clarify_intent(intent: dict, original_prompt: str) -> ClarificationResult:
    """
    Audit extracted intent for vagueness, conflicts, and missing info.

    Always returns a ClarificationResult — never blocks the pipeline.
    The result is attached to the API response so evaluators can see
    exactly what assumptions were made and why.

    Args:
        intent:          The dict output from extract_intent()
        original_prompt: The raw user prompt string

    Returns:
        ClarificationResult with documented assumptions and flags
    """
    raw = chain.invoke({
        "intent": intent,
        "original_prompt": original_prompt
    })

    try:
        return ClarificationResult(
            is_clear=raw.get("is_clear", True),
            clarity_score=int(raw.get("clarity_score", 7)),
            ambiguities=raw.get("ambiguities", []),
            conflicts=raw.get("conflicts", []),
            assumptions=raw.get("assumptions", []),
            clarifying_questions=raw.get("clarifying_questions", [])
        )
    except Exception as e:
        # Fallback: don't crash the pipeline, document the failure
        print(f"Clarification parse error: {e}")
        return ClarificationResult(
            is_clear=True,
            clarity_score=5,
            ambiguities=["Clarification stage encountered a parsing error"],
            conflicts=[],
            assumptions=["Proceeding with best-effort interpretation"],
            clarifying_questions=[]
        )