from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from pydantic import ValidationError
from pipeline.models.schema_models import (
     DesignSchema,
     Permission
     )

parser = JsonOutputParser()

prompt_template = PromptTemplate(
    template="""
You are a software system architect AI.

Your task is to convert structured app intent into
a software architecture design.

Generate:
- entities
- flows
- roles
- permissions

Return ONLY valid JSON.

Intent:
{intent}

Example Output:
{{
  "entities": ["User", "Contact"],
  "flows": ["login", "manage_contacts"],
  "roles": ["admin", "user"],
  "permissions": [
    {{
      "role": "admin",
      "access": ["dashboard", "analytics"]
    }},
    {{
      "role": "user",
      "access": ["basic_features"]
    }}
  ]
}}
""",
    input_variables=["intent"]
)

chain = prompt_template | llm | parser


def design_system(intent):
    result = chain.invoke({
        "intent": intent
    })

    try:

        validated_result = DesignSchema(
            entities=result.get("entities", []),
            flows=result.get("flows", []),
            roles=result.get("roles", []),
            permissions=[
                Permission(**permission)
                for permission in result.get("permissions", [])
            ]
        )
        return validated_result

    except ValidationError as e:

        print("Validation Error:")
        print(e)

        return None