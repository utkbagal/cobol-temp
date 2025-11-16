# Agentic AI Developer Capstone Project  
## Domain: Insurance (Enterprise Claims & Policy Operations)  
## Project Title: **Multi‑Agent Claims Intelligence System (MACIS)**  

---

# 1. Introduction  
Insurance is a domain with complex document processing, high operational workload, legacy systems, and strong compliance requirements.  
The Developer Capstone challenges learners to build an **end-to-end multi-agent system** with:  
- RAG  
- Tool calling  
- FastAPI backend  
- Streamlit/Gradio UI  
- Vector DB + DBMS/NoSQL  
- Dockerized local deployment  
- Observability via Azure Application Insights  
- Secure configuration (dotenv)  
- Modular Python engineering  

This reflects true enterprise-level agent development work.

---

# 2. Problem Statement  
Insurance companies manually process:  
- Claims documents  
- Policy documents  
- Customer communications  
- Investigation notes  
- Adjuster reports  

This causes slow turnaround time, human errors, inconsistent risk evaluation, and compliance gaps.

The goal is to design and develop a **Multi‑Agent Claims Intelligence System (MACIS)** that:  
1. Performs document understanding through RAG  
2. Extracts structured information from user uploads  
3. Performs claim triage classification  
4. Generates compliance-safe summaries  
5. Calls external APIs/tools for policy lookup and claim-status updates  
6. Provides a clean UI for adjusters  
7. Logs all operations for auditibility  
8. Runs end‑to‑end on Docker with modular services  

---

# 3. Scope of the Capstone  

### In-Scope  
- Full-stack development (FastAPI backend + Streamlit/Gradio frontend)  
- Multi-agent workflow implementation  
- RAG pipeline design  
- Vector DB + NoSQL/SQL database integration  
- Azure App Insights logging  
- Docker containerization  
- Secure configuration with `.env`  
- Documentation and design decisions  

### Out-of-Scope  
- Real payment gateway or actual insurance systems  
- Live PHI/PII usage  
- Cloud deployment  

---

# 4. Functional Requirements  

### 4.1 Document Upload & Preprocessing  
- Accept PDF, TXT, or DOCX  
- Perform chunking + embedding  
- Index into Vector DB  

### 4.2 Claims AI Assistants (Multi-Agent Workflow)

#### 1. **Intake Agent**  
- Reads uploaded documents  
- Extracts metadata: Claimant name, incident date, policy ID, loss type  
- Detects missing fields  
- Calls **Policy Lookup Tool**

#### 2. **Compliance Agent**  
- Verifies whether required documentation is present  
- Flags compliance risks  
- Uses RAG to support evidence from policy terms  

#### 3. **Summarization Agent**  
- Generates claim summaries  
- Provides reasoning steps (safe, non-diagnostic)  

#### 4. **Risk Triage Agent**  
- Classifies claim risk (low/medium/high)  
- Gives rationale grounded in retrieved policy text  

All agents must communicate via shared memory or a controller.

### 4.3 Tools (API Endpoints)**  
Tools must be implemented via FastAPI or mocked services:

- **Policy Lookup Tool** (GET /policy/{id})  
- **Claim Status Tool** (GET/POST)  
- **Knowledge Base Retrieval Tool**  
- **Notification Service (e.g., send message to adjuster)**  

### 4.4 Front End  
- Streamlit or Gradio  
- Document upload  
- Show multi-agent conversation  
- Show extracted metadata & summary  
- Show risk classification  

---

# 5. Non-Functional Requirements  

### 5.1 Security & Compliance  
- Input sanitization  
- No PHI/PII leaks  
- Prompt guardrails  
- Strict tool‑input schema validation  
- `.env` for secrets  
- Encryption of storage (if DB used)

### 5.2 Observability  
Mandatory:  
- Integration with Azure App Insights  
- Log: Prompt, completion, latency, tool calls  
- Correlation ID for full request lifecycle  
- Custom events: `AGENT_DECISION`, `RAG_HIT`, `TOOL_INVOCATION`  

### 5.3 Reliability  
- Graceful fallback when LLM/tool fails  
- Timeout and retry logic  

### 5.4 Performance  
- Latency target < 8 seconds end-to-end  
- Streaming output enabled  

---

# 6. Architecture Requirements  

The architecture MUST include:

### 6.1 System Components  
- Frontend (Streamlit or Gradio)  
- FastAPI Backend (Core)  
- Multi-Agent Orchestrator  
- RAG Engine  
- Vector DB (Chroma / MongoDB Atlas Vector / pgvector, learner chooses)  
- DB (MongoDB/Postgres/etc.)  
- Logging Layer  
- Docker Container Setup  

### 6.2 Suggested Folder Structure  
```
/app
    /api
    /agents
    /rag
    /db
    /tools
    /utils
    /config
    main.py
/frontend
    ui.py
/docker
.env.example
README.md
```

### 6.3 Microservice Components  
You **must implement at least 2 services**:  
- Core service (FastAPI + Agents + RAG)  
- UI service (Streamlit/Gradio)  

Optional 3rd service:  
- Policy API mock service  

### 6.4 RAG Requirements  
- Chunking strategy must be justified  
- Metadata filtering must be implemented  
- Hybrid retrieval recommended (vector + keyword)  
- Embeddings must be chosen & justified  

### 6.5 Database Requirements  
Learners must choose ANY:  
- MongoDB (document storage + metadata)  
- Postgres (structured metadata + pgvector)  

They must justify their choice.  

---

# 7. Topics Developers Must Answer  

Each participant must document:

### 7.1 Why OpenAI and Not On-Prem LLM?  
Consider:  
- Latency  
- Cost  
- Safety  
- Accuracy  
- Domain alignment  
- Model freshness  
- Hardware requirements  

### 7.2 RAG Pipeline Design  
- Why chosen chunk method (recursive, sentence-based, custom)?  
- Why chosen Vector DB?  
- Embedding choice justification  
- Re-ranking strategy (optional)

### 7.3 Tool Design Strategy  
- Tool schemas and validation patterns  
- Error-handling rules  
- Retry + backoff  
- Idempotency  

### 7.4 Multi-Agent Strategy  
- Why multi-agent vs single agent  
- Memory sharing patterns  
- Controller logic  

### 7.5 Backend Engineering Justifications  
- Why FastAPI?  
- Async vs Sync components  
- How routing & dependency injection work  
- Background tasks  
- Modular code organization  

### 7.6 Frontend Engineering Justifications  
- Why Streamlit or Gradio?  
- UI architecture choices  
- State management strategy  

### 7.7 Database Choices  
Developers must justify:  
- Relational vs NoSQL  
- How metadata is stored  
- Vector DB integration strategy  

### 7.8 Observability Plan  
- What metrics  
- What KQL queries  
- Which failures to alert on  

### 7.9 Docker & Local Deployment  
- Multi-container design  
- Dockerfile optimization  
- Environment config strategy  

---

# 8. Expected Best Practices  

### 8.1 Python Best Practices  
- Modularized code  
- Pydantic models  
- dotenv for config  
- Clear exceptions  
- Custom logging middleware  
- Async FastAPI endpoints  

### 8.2 Agent Development Best Practices  
- Use deterministic prompts  
- Guardrail patterns (regex, deny lists, safety prompts)  
- Memory summarization  
- Observation-action architecture  

### 8.3 RAG Best Practices  
- Avoid over-chunking  
- Use metadata filters  
- Resolve retrieval hallucinations with cross-checks  
- Deduplicate documents  
- Track RAG hit rate  

### 8.4 Backend/API Best Practices  
- Versioned endpoints  
- OpenAPI schema  
- Pydantic schema validation  
- Timeout policies  
- Instrumentation middleware  

### 8.5 Frontend Best Practices  
- Clear UX with loading states  
- No direct LLM calls from UI  
- Use backend endpoints only  
- Session state for multi-turn  
- Sanitized user input  

### 8.6 Docker Best Practices  
- Multi-stage Dockerfile  
- Avoid unnecessary packages  
- .dockerignore usage  
- Config mount for .env  
- Health checks  

---

# 9. Evaluation Rubric  

| Category | Weight | Criteria |
|---------|--------|----------|
| **Code Quality & Modularity** | 20% | Folder structure, readability, modular design |
| **Multi-Agent Workflow** | 20% | Controller logic, memory sharing, coordination |
| **RAG Implementation** | 15% | Chunking, embeddings, filtering, retrieval accuracy |
| **Tools & APIs** | 15% | Proper schemas, error handling, retries |
| **Frontend Integration** | 10% | Clean UI, aligned with backend, usable flow |
| **Observability & Logging** | 10% | Azure logs, structured events, correlation IDs |
| **Dockerization** | 5% | Working multi-container setup |
| **Documentation** | 5% | Clarity, architecture decisions, tech justification |

Total: **100%**

---

# 10. Future Enhancements  

Developers must propose at least 5 enhancements from:  

1. Multi-Agent Planning (CrewAI-like planner)  
2. Add LLM-based policy comparison module  
3. Add claim fraud detection ML model  
4. Add policy language simplification agent  
5. Add multi-turn conversational interface  
6. Add Redis caching for embeddings  
7. Add semantic search on structured DB  
8. Add PDF extraction agent using image models  

---

# 11. Submission Requirements  

- Architecture Document (PDF + Diagrams)  
- RAG Pipeline Document  
- Multi-Agent Workflow Document  
- Backend Code (FastAPI)  
- Frontend Code (Streamlit/Gradio)  
- Docker Setup (docker-compose.yml)  
- Observability Design  
- README (Setup + Usage)  

---

# End of Document
