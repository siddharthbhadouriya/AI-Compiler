from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm

parser = JsonOutputParser()

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

chain = prompt_template | llm | parser


def extract_intent(user_prompt: str):
    result = chain.invoke({
        "input": user_prompt
    })

    return result