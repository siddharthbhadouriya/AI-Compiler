import json
from pipeline.models.schema_models import AppSchema
from typing import List


# ---------------------------------------------------------------------------
# Each check returns a list of error strings.
# An empty list means that check passed.
# ---------------------------------------------------------------------------

def _check_schema_serializable(schema: AppSchema) -> List[str]:
    """
    Rule: The entire schema must be serializable to valid JSON at any point.
    Why: The PDF requires 'valid JSON always'. Even if Pydantic accepted the
         object, nested objects could contain types that break serialization.
         This is the final JSON safety net.
    """
    errors = []
    try:
        json.dumps(schema.model_dump())
    except (TypeError, ValueError) as e:
        errors.append(
            f"[JSON] Schema failed JSON serialization check: {str(e)}"
        )
    return errors


def _check_required_fields_present(schema: AppSchema) -> List[str]:
    """
    Rule: Core sections (db, api, ui, auth) must not be empty.
    Why: An empty schema is a silent failure — the pipeline produced nothing.
    """
    errors = []
    if not schema.db_schema:
        errors.append("[MISSING] db_schema is empty.")
    if not schema.api_schema:
        errors.append("[MISSING] api_schema is empty.")
    if not schema.ui_schema:
        errors.append("[MISSING] ui_schema is empty.")
    if not schema.auth_schema:
        errors.append("[MISSING] auth_schema is empty.")
    return errors


def _check_db_field_types(schema: AppSchema) -> List[str]:
    """
    Rule: Every DB field's type must be one of the allowed primitives.
    Why: Hallucinated types like 'uuid', 'Number', 'varchar' will break
         ORM code-generators. Only our 5 known types are safe.
    """
    ALLOWED_TYPES = {"string", "integer", "boolean", "datetime", "text"}
    errors = []

    for entity in schema.db_schema:
        for field in entity.fields:
            if field.type not in ALLOWED_TYPES:
                errors.append(
                    f"[DB] Entity '{entity.name}' → field '{field.name}' "
                    f"has invalid type '{field.type}'. "
                    f"Allowed: {ALLOWED_TYPES}"
                )
    return errors


def _check_api_entities_exist_in_db(schema: AppSchema) -> List[str]:
    """
    Rule: Every API route's 'entity' must reference a real DB entity.
    Why: API fields must match DB schema (PDF requirement).
         An API pointing to a non-existent table crashes at runtime.
    """
    errors = []
    db_entity_names = {e.name for e in schema.db_schema}

    for route in schema.api_schema:
        if route.entity and route.entity not in db_entity_names:
            errors.append(
                f"[API→DB] Route '{route.path}' references entity "
                f"'{route.entity}' which does not exist in db_schema. "
                f"Known entities: {db_entity_names}"
            )
    return errors


def _check_ui_routes_exist_in_api(schema: AppSchema) -> List[str]:
    """
    Rule: Every API route referenced by a UI page must exist in api_schema.
    Why: UI fields must map to API (PDF requirement).
         A frontend calling a missing endpoint = 404 in production.
    """
    errors = []
    api_paths = {r.path for r in schema.api_schema}

    for component in schema.ui_schema:
        for route in component.api_routes:
            if route not in api_paths:
                errors.append(
                    f"[UI→API] Page '{component.page}' calls route '{route}' "
                    f"which does not exist in api_schema. "
                    f"Known paths: {api_paths}"
                )
    return errors


def _check_roles_consistent(schema: AppSchema) -> List[str]:
    """
    Rule: Every role used in API routes or UI pages must have an auth rule.
    Why: Undeclared roles mean no permission policy — a security hole.
         This catches logical inconsistencies across layers (PDF requirement).
    """
    errors = []
    auth_roles = {a.role for a in schema.auth_schema}

    used_roles: set = set()
    for route in schema.api_schema:
        used_roles.update(route.roles)
    for component in schema.ui_schema:
        used_roles.update(component.accessible_by)

    for role in used_roles:
        if role not in auth_roles:
            errors.append(
                f"[AUTH] Role '{role}' is used in api/ui schemas but has no "
                f"entry in auth_schema. Add a rule for it."
            )
    return errors


def _check_api_methods_valid(schema: AppSchema) -> List[str]:
    """
    Rule: Every API route's method must be a standard HTTP verb.
    Why: Hallucinated methods like 'FETCH' or 'SEND' are not real HTTP.
         This catches hallucinated fields (PDF requirement).
    """
    ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}
    errors = []

    for route in schema.api_schema:
        if route.method.upper() not in ALLOWED_METHODS:
            errors.append(
                f"[API] Route '{route.path}' has invalid HTTP method "
                f"'{route.method}'. Allowed: {ALLOWED_METHODS}"
            )
    return errors


def _check_auth_permissions_valid(schema: AppSchema) -> List[str]:
    """
    Rule: Auth permissions must only be from the known set.
    Why: Invented permissions like 'superuser' or 'god_mode' are meaningless
         to the runtime. Catches hallucinated fields in auth layer.
    """
    ALLOWED_PERMISSIONS = {"read", "write", "delete", "admin"}
    errors = []

    for rule in schema.auth_schema:
        for perm in rule.permissions:
            if perm not in ALLOWED_PERMISSIONS:
                errors.append(
                    f"[AUTH] Role '{rule.role}' has unknown permission "
                    f"'{perm}'. Allowed: {ALLOWED_PERMISSIONS}"
                )
    return errors


# ---------------------------------------------------------------------------
# Public result object
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self, errors: List[str]):
        self.errors = errors
        self.is_valid = len(errors) == 0

    def __repr__(self):
        if self.is_valid:
            return "ValidationResult(PASSED ✅)"
        return f"ValidationResult(FAILED ❌, {len(self.errors)} errors)"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_schema(schema: AppSchema) -> ValidationResult:
    """
    Run all validation checks on a fully generated AppSchema.

    Checks (in order of importance):
      1. JSON serializability     — PDF: 'valid JSON always'
      2. Required fields present  — PDF: 'required fields present'
      3. DB field type safety     — PDF: 'type safety' + 'hallucinated fields'
      4. API HTTP method validity — PDF: 'hallucinated fields'
      5. API → DB consistency     — PDF: 'API fields must match DB schema'
      6. UI → API consistency     — PDF: 'UI fields must map to API'
      7. Role consistency         — PDF: 'logical inconsistencies'
      8. Auth permission validity — PDF: 'hallucinated fields' in auth layer

    Returns a ValidationResult with all errors listed.
    Repair engine uses the error tags ([DB], [API→DB], [UI→API], [AUTH],
    [MISSING], [JSON]) to decide which layer to fix.
    """
    all_errors: List[str] = []

    all_errors += _check_schema_serializable(schema)
    all_errors += _check_required_fields_present(schema)
    all_errors += _check_db_field_types(schema)
    all_errors += _check_api_methods_valid(schema)
    all_errors += _check_api_entities_exist_in_db(schema)
    all_errors += _check_ui_routes_exist_in_api(schema)
    all_errors += _check_roles_consistent(schema)
    all_errors += _check_auth_permissions_valid(schema)

    if all_errors:
        print(f"\n⚠️  Validation found {len(all_errors)} issue(s):")
        for err in all_errors:
            print(f"  • {err}")
    else:
        print("\n✅ Validation passed — schema is consistent.")

    return ValidationResult(all_errors)