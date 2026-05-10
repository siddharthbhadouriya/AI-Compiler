from pipeline.design import design_system
from pipeline.intent import extract_intent
intent = extract_intent(
    "Build CRM with login, contacts and admin dashboard"
)

design= design_system(intent)
print (intent, "\n") 
print(design)

