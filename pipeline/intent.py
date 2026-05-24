from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from pydantic import BaseModel
from typing import List

parser = JsonOutputParser()

# Creating pydantic validation for JSON data
class IntentSchema (BaseModel):
    features : List[str]
    roles : List[str]

# using langchain for prompt
prompt_template = PromptTemplate(
    template="""
You are an AI intent extraction engine.

Extract:
- features
- roles

Return ONLY valid JSON.

User Request:
{input}

Example Output:
{{
    "features": ["auth", "dashboard"],
    "roles": ["admin", "user"]
}}
""",
    input_variables=["input"]
)

# using Chaining concept 
chain = prompt_template | llm | parser


def extract_intent(user_prompt: str):
    result = chain.invoke({
        "input": user_prompt
    })

    return result