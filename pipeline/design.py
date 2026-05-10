from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm

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

    return result