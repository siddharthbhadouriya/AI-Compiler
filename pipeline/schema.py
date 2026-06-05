from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from pydantic import ValidationError
from pipeline.models.schema_models import (
    APIRoute, AppSchema,AuthRule,DBEntity,DBField,UIComponent
)

parser = JsonOutputParser()

prompt_template = PromptTemplate(
    template="""
You are a schema generation engine for a compiler-style AI platform.

Convert this system design into a complete, cross-consistent application schema.

STRICT RULES:
- db_schema field types MUST be one of: string, integer, boolean, datetime, text
- api_schema entity MUST match a name in db_schema
- ui_schema api_routes MUST match paths in api_schema
- auth_schema MUST have a rule for every role in the design
- Return ONLY valid JSON, no explanation

Design:
{design}

Output format:
{{
  "db_schema": [
    {{
      "name": "User",
      "fields": [
        {{"name": "id", "type": "integer", "required": true}},
        {{"name": "email", "type": "string", "required": true}},
        {{"name": "role", "type": "string", "required": true}}
      ]
    }}
  ],
  "api_schema": [
    {{
      "path": "/api/auth/login",
      "method": "POST",
      "description": "Authenticate user and return token",
      "roles": ["admin", "user"],
      "entity": "User"
    }}
  ],
  "ui_schema": [
    {{
      "page": "LoginPage",
      "components": ["LoginForm", "ErrorMessage"],
      "accessible_by": ["admin", "user"],
      "api_routes": ["/api/auth/login"]
    }}
  ],
  "auth_schema": [
    {{"role": "admin", "permissions": ["read", "write", "delete", "admin"]}},
    {{"role": "user", "permissions": ["read", "write"]}}
  ]
}}
""",
    input_variables=["design"]
)
chain  = prompt_template | llm | parser

def  generate_schema(design):
    result = chain.invoke({"design": design.model_dump()})

    try:
        validated = AppSchema(
            db_schema=[
                DBEntity(
                    name=e["name"],
                    fields=[DBField(**f) for f in e.get("fields", [])]
                )
                for e in result.get("db_schema", [])
            ],
            api_schema=[APIRoute(**r) for r in result.get("api_schema", [])],
            ui_schema=[UIComponent(**u) for u in result.get("ui_schema", [])],
            auth_schema=[AuthRule(**a) for a in result.get("auth_schema", [])]
        )
        return validated

    except ValidationError as e:
        print("Schema Validation Error:", e)
        return None