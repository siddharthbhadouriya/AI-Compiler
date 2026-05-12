from fastapi import FastAPI
from pydantic import BaseModel
from pipeline.intent import extract_intent
from pipeline.design import design_system

class CompileRequest(BaseModel):
    prompt: str



app = FastAPI()  #app works as controller of server

@app.post("/compile")
def compile_app(request : CompileRequest):
    intent = extract_intent(request.prompt)
    design = design_system(intent)

    return {
        "intent": intent,
        "design": design,
    }



@app.get("/")
def home():
    return {"message": "Server is running"}