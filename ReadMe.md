# 🤖 Compylr AI

## Turning Natural Language into Reliable Software Systems

Compylr AI is a compiler-style AI platform that transforms natural language product requirements into structured, validated, and executable full-stack application configurations.

Instead of directly generating code from prompts, Compylr AI follows a deterministic multi-stage pipeline inspired by traditional compiler architecture:

```text
Natural Language
        ↓
Intent Extraction
        ↓
Architecture Planning
        ↓
Schema Generation
        ↓
Validation & Repair
        ↓
Executable Application Config
```

Built for reliable AI-driven software generation with execution awareness, schema consistency, and modular reasoning pipelines.

---

# 🚀 Overview

Modern AI systems often rely on:

```text
Prompt → Code
```

This approach is fast but unreliable.

Compylr AI introduces a structured engineering workflow:

```text
Prompt
  ↓
Intent Understanding
  ↓
System Design
  ↓
Schema Generation
  ↓
Validation
  ↓
Repair
  ↓
Executable Output
```

The platform behaves more like a compiler than a chatbot.

Its goal is to generate:

- Predictable outputs
- Structured configurations
- Execution-ready systems
- Reliable application architecture

---

# 🧠 What Compylr AI Generates

Given a prompt like:

```text
Build a CRM with login, contacts, role-based access, analytics dashboard and premium subscriptions.
```

Compylr AI generates:

- ✅ UI schema
- ✅ API schema
- ✅ Database schema
- ✅ Authentication rules
- ✅ Business logic
- ✅ Role permissions
- ✅ Execution-aware configurations

---

# 🏗️ System Architecture

```text
┌────────────────────┐
│  User Prompt Input │
└─────────┬──────────┘
          ↓
┌─────────────────────┐
│ Intent Extraction   │
│ (LLM + Parsing)     │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ System Design Layer │
│ (AI Architecture)   │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Schema Generator    │
│ UI/API/DB/Auth      │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Validation Engine   │
│ Type & Logic Checks │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Repair Engine       │
│ Auto Error Fixing   │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Executable Runtime  │
└─────────────────────┘
```

---

# ⚙️ Tech Stack

## Backend

- Python
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [LangChain](https://www.langchain.com/)

## AI Infrastructure

- Groq API
- LLM-based reasoning pipeline
- Structured prompt orchestration

## Validation System

- Pydantic schema enforcement
- Cross-layer consistency validation
- Deterministic output verification

---

# 🧩 Multi-Stage Compiler Pipeline

## 1️⃣ Intent Extraction

Extracts structured application intent from natural language.

### Input

```text
Build a CRM with login and admin analytics dashboard
```

### Output

```json
{
  "features": ["auth", "dashboard", "contacts", "analytics"],
  "roles": ["admin", "user"]
}
```

This stage focuses on semantic understanding of user requirements.

---

## 2️⃣ System Design Layer

Converts intent into architecture-level planning.

### Generates

- Entities
- Workflows
- Permissions
- Application structure

### Example

```json
{
  "entities": ["User", "Contact"],
  "flows": [
    "login",
    "manage_contacts",
    "view_dashboard"
  ],
  "permissions": [
    {
      "role": "admin",
      "access": ["analytics"]
    }
  ]
}
```

This acts as the architectural planner of the pipeline.

---

## 3️⃣ Schema Generation

Transforms architecture into executable configurations.

### Generated Layers

- UI configuration
- API schema
- Database schema
- Authentication schema

### Example

```json
{
  "db_schema": {
    "User": {
      "id": "integer",
      "email": "string"
    }
  }
}
```

---

## 4️⃣ Validation Engine

Ensures reliability and consistency across all generated layers.

### Validation Checks

- ✅ Valid JSON
- ✅ Required fields present
- ✅ Type safety
- ✅ API ↔ DB consistency
- ✅ UI ↔ API mapping
- ✅ Permission validation
- ✅ Entity reference validation

This stage ensures deterministic and production-safe outputs.

---

## 5️⃣ Repair Engine

Automatically detects and fixes:

- Invalid JSON
- Missing fields
- Hallucinated properties
- Schema mismatches
- Logical inconsistencies

Instead of regenerating the entire application blindly, Compylr AI repairs only broken sections.

This significantly improves:

- Reliability
- Latency
- Output consistency

---

# 🔥 Why This Project Is Different

Most AI generators stop at:

```text
Prompt → Response
```

Compylr AI focuses on:

```text
Reasoning
  +
Validation
  +
Repair
  +
Execution Awareness
```

The project is designed like a real AI infrastructure system rather than a simple prompt wrapper.

---

# 🛡️ Why LangChain?

LangChain is used for:

- Multi-stage orchestration
- Modular AI pipelines
- Structured prompt management
- Output parsing
- Deterministic workflow design

Instead of relying on a single large prompt, the platform uses separate reasoning stages for better control and reliability.

---

# 🧱 Why Pydantic?

Pydantic provides:

- Strict schema contracts
- Type enforcement
- Validation layers
- Predictable structured outputs

This enables deterministic behavior throughout the compiler pipeline.

---

# 📂 Project Structure

```text
Compylr-AI/
│
├── app/
│   ├── main.py
│   └── routes/
│
├── pipeline/
│   ├── intent.py
│   ├── design.py
│   ├── schema.py
│   ├── validate.py
│   └── repair.py
│
├── models/
│   └── schemas.py
│
├── runtime/
│   └── executor.py
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# 🚀 Features

- ✅ Compiler-style AI pipeline
- ✅ Multi-stage reasoning architecture
- ✅ Deterministic validation system
- ✅ Intelligent repair engine
- ✅ Structured schema generation
- ✅ Execution-aware outputs
- ✅ Cross-layer consistency checking
- ✅ Modular AI infrastructure

---

# ▶️ Running the Project

## Clone Repository

```bash
git clone https://github.com/your-username/compylr-ai.git
cd compylr-ai
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

---

# 🧪 Evaluation Framework

The platform evaluates:

- Success rate
- Retry count
- Validation failures
- Latency
- Consistency
- Repair frequency

It is also designed to handle:

- Vague prompts
- Conflicting requirements
- Incomplete instructions

---

# 🎯 Core Engineering Concepts

This project explores:

- AI orchestration systems
- Compiler-inspired architecture
- Structured generation pipelines
- Deterministic AI workflows
- Validation engineering
- Repair-based reliability systems
- Execution-aware AI infrastructure

---

# 🔮 Future Improvements

- Runtime application generation
- Frontend code generation
- Docker deployment
- Kubernetes orchestration
- Vector memory / RAG
- Streaming execution pipeline
- Multi-agent repair systems
- SaaS deployment architecture


---

# 👨‍💻 Author

## Siddharth Singh Bhadouriya

AI Systems & Infrastructure Builder  
Focused on reliable, execution-aware, compiler-style AI architectures.
