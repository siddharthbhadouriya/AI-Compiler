import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from pipeline.Validate import ValidationResult, validate_schema
from pipeline.models.schema_models import (
    AppSchema, DBEntity, DBField, APIRoute, UIComponent, AuthRule
)
from pydantic import ValidationError
from typing import List

parser = JsonOutputParser()

MAX_REPAIR_ATTEMPTS = 3

# ---------------------------------------------------------------------------
# Targeted repair prompts — one per broken layer
# ---------------------------------------------------------------------------

_DB_REPAIR_PROMPT = PromptTemplate(
    template="""
You are a database schema repair engine.

The current db_schema has these errors:
{errors}

Current db_schema:
{current}

Fix ONLY the db_schema. Rules:
- field types MUST be one of: string, integer, boolean, datetime, text
- every entity must have at least an 'id' field of type 'integer'
- return ONLY valid JSON, no explanation

Output format:
[
  {{
    "name": "EntityName",
    "fields": [
      {{"name": "id", "type": "integer", "required": true}},
      {{"name": "field_name", "type": "string", "required": true}}
    ]
  }}
]
""",
    input_variables=["errors", "current"]
)

_API_REPAIR_PROMPT = PromptTemplate(
    template="""
You are an API schema repair engine.

The current api_schema has these errors:
{errors}

Current api_schema:
{current}

Known DB entities (your routes MUST reference one of these):
{db_entities}

Fix ONLY the api_schema. Rules:
- 'entity' field must match a name from the DB entities list
- 'method' must be GET, POST, PUT, or DELETE
- return ONLY valid JSON, no explanation

Output format:
[
  {{
    "path": "/api/resource",
    "method": "GET",
    "description": "...",
    "roles": ["admin", "user"],
    "entity": "EntityName"
  }}
]
""",
    input_variables=["errors", "current", "db_entities"]
)

_UI_REPAIR_PROMPT = PromptTemplate(
    template="""
You are a UI schema repair engine.

The current ui_schema has these errors:
{errors}

Current ui_schema:
{current}

Known API paths (your pages MUST only reference these):
{api_paths}

Fix ONLY the ui_schema. Rules:
- api_routes must only contain paths from the known API paths list
- return ONLY valid JSON, no explanation

Output format:
[
  {{
    "page": "PageName",
    "components": ["ComponentA"],
    "accessible_by": ["admin", "user"],
    "api_routes": ["/api/resource"]
  }}
]
""",
    input_variables=["errors", "current", "api_paths"]
)

_AUTH_REPAIR_PROMPT = PromptTemplate(
    template="""
You are an auth schema repair engine.

The current auth_schema has these errors:
{errors}

Current auth_schema:
{current}

All roles that MUST have an auth rule:
{required_roles}

Fix ONLY the auth_schema. Rules:
- every role in required_roles must have an entry
- permissions must be from: read, write, delete, admin
- return ONLY valid JSON, no explanation

Output format:
[
  {{"role": "admin", "permissions": ["read", "write", "delete", "admin"]}},
  {{"role": "user",  "permissions": ["read", "write"]}}
]
""",
    input_variables=["errors", "current", "required_roles"]
)


# ---------------------------------------------------------------------------
# Repair helpers — each fixes one layer
# ---------------------------------------------------------------------------

def _repair_db(schema: AppSchema, errors: List[str]) -> AppSchema:
    db_errors = [e for e in errors if "[DB]" in e or "[MISSING] db" in e]
    if not db_errors:
        return schema

    print("   Repairing db_schema...")
    chain = _DB_REPAIR_PROMPT | llm | parser
    result = chain.invoke({
        "errors": "\n".join(db_errors),
        "current": json.dumps([e.model_dump() for e in schema.db_schema], indent=2)
    })

    try:
        new_db = [
            DBEntity(name=e["name"], fields=[DBField(**f) for f in e.get("fields", [])])
            for e in result
        ]
        return schema.model_copy(update={"db_schema": new_db})
    except (ValidationError, Exception) as e:
        print(f"   DB repair failed: {e}")
        return schema


def _repair_api(schema: AppSchema, errors: List[str]) -> AppSchema:
    api_errors = [e for e in errors if "[API" in e or "[MISSING] api" in e]
    if not api_errors:
        return schema

    print("   Repairing api_schema...")
    db_entity_names = [e.name for e in schema.db_schema]
    chain = _API_REPAIR_PROMPT | llm | parser
    result = chain.invoke({
        "errors": "\n".join(api_errors),
        "current": json.dumps([r.model_dump() for r in schema.api_schema], indent=2),
        "db_entities": db_entity_names
    })

    try:
        new_api = [APIRoute(**r) for r in result]
        return schema.model_copy(update={"api_schema": new_api})
    except (ValidationError, Exception) as e:
        print(f"   API repair failed: {e}")
        return schema


def _repair_ui(schema: AppSchema, errors: List[str]) -> AppSchema:
    ui_errors = [e for e in errors if "[UI" in e or "[MISSING] ui" in e]
    if not ui_errors:
        return schema

    print("   Repairing ui_schema...")
    api_paths = [r.path for r in schema.api_schema]
    chain = _UI_REPAIR_PROMPT | llm | parser
    result = chain.invoke({
        "errors": "\n".join(ui_errors),
        "current": json.dumps([u.model_dump() for u in schema.ui_schema], indent=2),
        "api_paths": api_paths
    })

    try:
        new_ui = [UIComponent(**u) for u in result]
        return schema.model_copy(update={"ui_schema": new_ui})
    except (ValidationError, Exception) as e:
        print(f"   UI repair failed: {e}")
        return schema


def _repair_auth(schema: AppSchema, errors: List[str]) -> AppSchema:
    auth_errors = [e for e in errors if "[AUTH]" in e or "[MISSING] auth" in e]
    if not auth_errors:
        return schema

    print("  Repairing auth_schema...")

    # Collect all roles mentioned in the schema
    used_roles: set = set()
    for route in schema.api_schema:
        used_roles.update(route.roles)
    for component in schema.ui_schema:
        used_roles.update(component.accessible_by)

    chain = _AUTH_REPAIR_PROMPT | llm | parser
    result = chain.invoke({
        "errors": "\n".join(auth_errors),
        "current": json.dumps([a.model_dump() for a in schema.auth_schema], indent=2),
        "required_roles": list(used_roles)
    })

    try:
        new_auth = [AuthRule(**a) for a in result]
        return schema.model_copy(update={"auth_schema": new_auth})
    except (ValidationError, Exception) as e:
        print(f"  Auth repair failed: {e}")
        return schema


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def repair_schema(schema: AppSchema, validation: ValidationResult) -> AppSchema:
    """
    Surgically repair only the broken layers in the schema.

    Strategy:
      1. Look at which layers have errors.
      2. Re-prompt the LLM with ONLY that layer + its specific errors.
      3. Re-validate after each repair cycle.
      4. Stop when valid or when MAX_REPAIR_ATTEMPTS is reached.

    This is NOT a blind full retry — we fix only what's broken.
    """
    if validation.is_valid:
        print(" Schema is already valid — no repair needed.")
        return schema

    current_schema = schema

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        print(f"\n Repair attempt {attempt}/{MAX_REPAIR_ATTEMPTS}")

        errors = validation.errors

        # Repair layers in dependency order: DB first, then API, then UI, then Auth
        # (because API depends on DB, UI depends on API, Auth depends on roles in all)
        current_schema = _repair_db(current_schema, errors)
        current_schema = _repair_api(current_schema, errors)
        current_schema = _repair_ui(current_schema, errors)
        current_schema = _repair_auth(current_schema, errors)

        # Re-validate after repairs
        validation = validate_schema(current_schema)

        if validation.is_valid:
            print(f"\n Schema repaired successfully after {attempt} attempt(s).")
            return current_schema

    print(f"\n Could not fully repair schema after {MAX_REPAIR_ATTEMPTS} attempts.")
    print(f"   Remaining errors: {validation.errors}")
    return current_schema  # return best effort