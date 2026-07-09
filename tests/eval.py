"""
tests/eval.py

Evaluation Framework — spec requirement #7
───────────────────────────────────────────
The spec says (verbatim):
  "Create a dataset:
   - 10 real product prompts
   - 10 edge cases: vague, conflicting, incomplete
   Track: success rate, retries per request, failure types, latency"
  "Show actual metrics, not claims"

Run this directly:
  python tests/eval.py

Output: a printed table of results + a summary JSON saved to
tests/eval_results.json for your Loom video and submission.
"""

import time
import json
import sys
import os

# Make sure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.intent import extract_intent
from pipeline.clarify import clarify_intent
from pipeline.design import design_system
from pipeline.schema import generate_schema
from pipeline.Validate import validate_schema
from pipeline.repair import repair_schema
from runtime.executor import execute_schema


# ── Eval dataset ─────────────────────────────────────────────────────────────
# Exactly as specified: 10 real + 10 edge cases

REAL_PROMPTS = [
    {
        "id": "R01",
        "category": "real",
        "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    },
    {
        "id": "R02",
        "category": "real",
        "prompt": "Create a project management tool like Trello with boards, cards, team collaboration, and user authentication."
    },
    {
        "id": "R03",
        "category": "real",
        "prompt": "Build an e-commerce platform with product listings, shopping cart, Stripe payments, order tracking, and admin panel."
    },
    {
        "id": "R04",
        "category": "real",
        "prompt": "Create a blog platform where users can write posts, comment, follow other writers, and subscribe to newsletters."
    },
    {
        "id": "R05",
        "category": "real",
        "prompt": "Build a restaurant booking system with table management, reservations, customer profiles, and SMS confirmations."
    },
    {
        "id": "R06",
        "category": "real",
        "prompt": "Create a learning management system with courses, video lessons, quizzes, progress tracking, and certificates."
    },
    {
        "id": "R07",
        "category": "real",
        "prompt": "Build a SaaS analytics dashboard with user authentication, data visualizations, team workspaces, and API access."
    },
    {
        "id": "R08",
        "category": "real",
        "prompt": "Create a freelancer marketplace with client and freelancer roles, job postings, proposals, escrow payments, and reviews."
    },
    {
        "id": "R09",
        "category": "real",
        "prompt": "Build a healthcare appointment system with patient profiles, doctor schedules, appointment booking, and prescription records."
    },
    {
        "id": "R10",
        "category": "real",
        "prompt": "Create a social media app with posts, likes, comments, follow system, notifications, and direct messaging."
    },
]

EDGE_CASE_PROMPTS = [
    {
        "id": "E01",
        "category": "vague",
        "subtype": "vague",
        "prompt": "build an app"
    },
    {
        "id": "E02",
        "category": "edge",
        "subtype": "vague",
        "prompt": "make something useful for businesses"
    },
    {
        "id": "E03",
        "category": "edge",
        "subtype": "conflicting",
        "prompt": "Build a completely free platform with no ads that makes money through premium subscriptions and one-time payments."
    },
    {
        "id": "E04",
        "category": "edge",
        "subtype": "conflicting",
        "prompt": "Create a social network where users have full privacy — no data stored, but with personalised recommendations and targeted ads."
    },
    {
        "id": "E05",
        "category": "edge",
        "subtype": "incomplete",
        "prompt": "Build a system to manage our inventory."
    },
    {
        "id": "E06",
        "category": "edge",
        "subtype": "incomplete",
        "prompt": "Make a dashboard with charts and reports."
    },
    {
        "id": "E07",
        "category": "edge",
        "subtype": "vague",
        "prompt": "Build an app like Uber but better."
    },
    {
        "id": "E08",
        "category": "edge",
        "subtype": "conflicting",
        "prompt": "Build an admin panel with no admin role, where all users have full access to everything but no user can delete anything."
    },
    {
        "id": "E09",
        "category": "edge",
        "subtype": "incomplete",
        "prompt": "Create a marketplace."
    },
    {
        "id": "E10",
        "category": "edge",
        "subtype": "overspecified",
        "prompt": "Build a CRM with 47 custom fields per contact, real-time sync across 12 devices, AI auto-fill, blockchain audit log, voice commands, AR interface, and offline mode that syncs when reconnected."
    },
]

ALL_PROMPTS = REAL_PROMPTS + EDGE_CASE_PROMPTS


# ── Single prompt runner ──────────────────────────────────────────────────────

def run_single(entry: dict) -> dict:
    """Run one prompt through the full pipeline and return metrics."""
    start = time.time()
    result = {
        "id":             entry["id"],
        "category":       entry["category"],
        "subtype":        entry.get("subtype", "—"),
        "prompt_preview": entry["prompt"][:60] + ("..." if len(entry["prompt"]) > 60 else ""),
        "success":        False,
        "clarity_score":  None,
        "conflicts":      0,
        "assumptions":    0,
        "retry_count":    0,
        "failure_type":   None,
        "validation_errors": 0,
        "entities":       0,
        "endpoints":      0,
        "executable":     False,
        "latency_ms":     0,
        "error":          None,
    }

    try:
        # Stage 1: Intent
        intent = extract_intent(entry["prompt"])
        if not intent:
            result["failure_type"] = "intent_extraction"
            return result

        # Stage 2: Clarification
        clarification = clarify_intent(intent, entry["prompt"])
        result["clarity_score"] = clarification.clarity_score
        result["conflicts"]     = len(clarification.conflicts)
        result["assumptions"]   = len(clarification.assumptions)

        # Stage 3: Design
        design = design_system(intent)
        if not design:
            result["failure_type"] = "system_design"
            return result

        # Stage 4: Schema
        schema = generate_schema(design)
        if not schema:
            result["failure_type"] = "schema_generation"
            return result

        # Stage 5: Validation
        validation = validate_schema(schema)
        result["validation_errors"] = len(validation.errors)

        # Stage 6: Repair loop
        retries = 0
        if not validation.is_valid:
            for _ in range(3):
                schema = repair_schema(schema, validation)
                validation = validate_schema(schema)
                retries += 1
                if validation.is_valid:
                    break

        result["retry_count"] = retries
        if not validation.is_valid:
            result["failure_type"] = "repair_exhausted"

        # Stage 7: Execution
        latency_ms = round((time.time() - start) * 1000, 1)
        exec_report = execute_schema(schema, latency_ms=latency_ms, retry_count=retries)

        result["entities"]   = len(schema.db_schema)
        result["endpoints"]  = len(schema.api_schema)
        result["executable"] = exec_report["health_check"]["executable"]
        result["success"]    = validation.is_valid
        if not result["failure_type"] and not result["success"]:
            result["failure_type"] = "validation_failed"

    except Exception as e:
        result["failure_type"] = f"exception: {type(e).__name__}"
        result["error"] = str(e)

    result["latency_ms"] = round((time.time() - start) * 1000, 1)
    return result


# ── Table printer ─────────────────────────────────────────────────────────────

def _col(val, width):
    s = str(val) if val is not None else "—"
    return s[:width].ljust(width)


def print_results_table(results: list[dict]):
    header = (
        f"{'ID':<4} {'Cat':<5} {'Sub':<12} {'OK':<3} "
        f"{'Clr':<4} {'Conf':<5} {'Asmp':<5} {'Rty':<4} "
        f"{'Ent':<4} {'Ep':<4} {'Exe':<4} "
        f"{'ms':<7} {'Failure':<25}"
    )
    print("\n" + "═" * len(header))
    print("  COMPYLR AI — EVALUATION RESULTS")
    print("═" * len(header))
    print(header)
    print("─" * len(header))

    for r in results:
        ok  = "✅" if r["success"] else "❌"
        exe = "✅" if r["executable"] else "❌"
        print(
            f"{_col(r['id'],4)} {_col(r['category'],5)} {_col(r['subtype'],12)} {ok:<3} "
            f"{_col(r['clarity_score'],4)} {_col(r['conflicts'],5)} {_col(r['assumptions'],5)} "
            f"{_col(r['retry_count'],4)} {_col(r['entities'],4)} {_col(r['endpoints'],4)} "
            f"{exe:<4} {_col(r['latency_ms'],7)} "
            f"{_col(r['failure_type'] or '',25)}"
        )

    print("═" * len(header))


def print_summary(results: list[dict]):
    total        = len(results)
    succeeded    = sum(1 for r in results if r["success"])
    real_ok      = sum(1 for r in results if r["category"] == "real" and r["success"])
    edge_ok      = sum(1 for r in results if r["category"] != "real" and r["success"])
    executable   = sum(1 for r in results if r["executable"])
    avg_latency  = sum(r["latency_ms"] for r in results) / total
    avg_retries  = sum(r["retry_count"] for r in results) / total
    avg_clarity  = sum(r["clarity_score"] for r in results if r["clarity_score"]) / total

    failure_types: dict = {}
    for r in results:
        if r["failure_type"]:
            failure_types[r["failure_type"]] = failure_types.get(r["failure_type"], 0) + 1

    print(f"\n{'─'*50}")
    print(f"  SUMMARY")
    print(f"{'─'*50}")
    print(f"  Total prompts:       {total}")
    print(f"  Success rate:        {succeeded}/{total} ({round(succeeded/total*100)}%)")
    print(f"  Real prompts:        {real_ok}/10")
    print(f"  Edge cases:          {edge_ok}/10")
    print(f"  Executable schemas:  {executable}/{total}")
    print(f"  Avg latency:         {round(avg_latency)}ms")
    print(f"  Avg retries:         {round(avg_retries, 2)}")
    print(f"  Avg clarity score:   {round(avg_clarity, 1)}/10")
    if failure_types:
        print(f"  Failure breakdown:")
        for ft, count in failure_types.items():
            print(f"    {ft}: {count}")
    print(f"{'─'*50}\n")

    return {
        "total": total,
        "success_rate_pct": round(succeeded / total * 100),
        "real_success": f"{real_ok}/10",
        "edge_success": f"{edge_ok}/10",
        "executable": executable,
        "avg_latency_ms": round(avg_latency),
        "avg_retries": round(avg_retries, 2),
        "avg_clarity_score": round(avg_clarity, 1),
        "failure_types": failure_types,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🧪 Compylr AI — Evaluation Framework")
    print("   Running 20 prompts (10 real + 10 edge cases)...\n")

    results = []
    for i, entry in enumerate(ALL_PROMPTS, 1):
        print(f"[{i:02d}/20] {entry['id']} — {entry['prompt'][:55]}...")
        r = run_single(entry)
        results.append(r)
        status = "✅" if r["success"] else "❌"
        print(f"       {status} {r['latency_ms']}ms | retries={r['retry_count']} | clarity={r['clarity_score']}")

    print_results_table(results)
    summary = print_summary(results)

    # Save full results to JSON
    output = {
        "summary":  summary,
        "results":  results,
    }
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"📄 Full results saved to: {out_path}")