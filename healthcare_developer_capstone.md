# Agentic AI Developer Capstone Project  
## Domain: Healthcare (Regulated Clinical Workflow Automation)  
## Project Title: **Intelligent Clinical Documentation & Care Workflow Agentic System (ICD-CWA)**  

---

# 1. Introduction
Healthcare is the most regulated and risk-sensitive domain, with stringent requirements around privacy, auditability, traceability, and accuracy of clinical information.  
Developers must build an **end‑to‑end multi‑agent clinical workflow system** adhering to healthcare compliance (HIPAA‑like constraints), RAG-based contextual intelligence, secure backend engineering, and modular architecture.

Unlike typical AI builds, this project must **demonstrate responsible AI engineering** suitable for clinical environments.

This document defines:
- Specifications  
- Functional & non-functional requirements  
- Compliance & guardrail expectations  
- Best practices  
- Engineering stack requirements  
- Evaluation criteria  

---

# 2. Problem Statement

Clinicians face:
- Overload of patient data scattered across EHR, labs, radiology, and internal notes  
- High administrative burden (summaries, referrals, handover notes)  
- Lack of unified view for care teams  
- Compliance-heavy reporting requirements  
- Human errors in manual documentation  

**Goal:**  
Build a system that processes clinical inputs (documents, lab results, notes) and assists clinical teams in generating **safe, compliant, structured, auditable documentation** through multi-agent workflows.

The system must:
1. Handle structured & unstructured clinical data  
2. Retrieve information from a knowledge base (SOPs, policies, care guidelines)  
3. Generate structured summaries  
4. Provide data-grounded reasoning using RAG  
5. Maintain compliance: logging, traceability, PHI minimization  
6. Handle multiple clinical assistants (agents) working together  
7. Run in Docker  
8. Include UI + API + Vector DB + Database  

---

# 3. System Overview

The **Intelligent Clinical Documentation & Care Workflow Agentic System (ICD-CWA)** includes:

### Assistant Agents (minimum required)
1. **Triage Agent**  
   Extracts key clinical metadata and identifies missing information.

2. **Clinical Summary Agent**  
   Creates SOAP notes / discharge summaries / clinical narratives.

3. **Risk & Compliance Agent**  
   Ensures documentation adheres to clinical policies, flags unsafe statements.

4. **Care Recommendation Agent**  
   Provides guideline-aligned next-step recommendations (non-diagnostic).

Agents must interact through a **controller agent** or orchestrator.

---

# 4. Functional Requirements

### 4.1 Data Ingestion
- File Upload (PDF, DOCX, TXT)
- Structured ingestion of lab results or vitals (JSON/CSV)
- Document splitting + metadata tagging

### 4.2 RAG Pipeline
- Chunking with justification  
- Metadata-aware retrieval (patient_id, visit_type, specialty)  
- Evidence-grounded responses  
- Retrieval confidence scoring  

### 4.3 Multi-Agent Processing
Each agent must:
- Accept structured inputs  
- Produce structured outputs  
- Log its decision + reasoning source  
- Use RAG for grounding  

### 4.4 Tools (APIs)
At least 3 tools must be implemented via FastAPI:
1. **EHR Lookup Tool** (mocked patient data)  
2. **Lab Retrieval Tool**  
3. **Clinical Guidelines Lookup Tool**  

### 4.5 Front End
- Streamlit or Gradio  
- Upload medical documents  
- Display agent conversation trace  
- Show summary, flagged risks, recommended actions  

### 4.6 Compliance Logging
- Log: Prompt, response, timestamp, tool calls, retrieved docs  
- Sensitive data masking at rest  
- Access logs for each user session  

---

# 5. Non-Functional Requirements

### 5.1 Compliance (Mandatory)
- PHI Minimization  
- Local-only processing (no external PHI transmission)  
- Strict schema validation  
- Explicit safe‑completion prompting  
- No clinical diagnosis  
- No hallucinated medical facts  
- Logging for audit trails  
- Consent simulation  
- Role-based context presentation  

### 5.2 Observability
- Azure App Insights  
- Custom events: `CLINICAL_SUMMARY`, `POLICY_VIOLATION`, `RAG_GROUNDING`, `TOOL_CALL`  
- Correlation ID across the entire workflow  

### 5.3 Security
- .env for secrets  
- Sanitized inputs  
- Safe tool schemas  
- Output filtering  

### 5.4 Performance
- End-to-end latency target: < 10 seconds  
- Streaming responses allowed  
- RAG cache recommended  

---

# 6. Architecture Requirements

### Required Components
- Multi-Agent Orchestrator  
- FastAPI Backend  
- Streamlit/Gradio UI  
- Vector DB (Chroma / MongoDB Vector / pgvector)  
- Database (MongoDB/Postgres)  
- Logging Layer  
- Compliance Scanner/Filters  
- Dockerized services  

### Microservices
Minimum:  
- **Core backend service** (agents + RAG + APIs)  
- **UI service**  
Optional:  
- **Guidelines mock service**  

### Folder Structure
```
/app
    /agents
    /api
    /rag
    /compliance
    /utils
    /config
    main.py
/frontend
    ui.py
/docker
.env.example
README.md
```

---

# 7. Required Documentation Sections (Developer Must Answer)

### 7.1 Why OpenAI and Not On-Prem LLM?
Address:
- Regulatory risk  
- Hardware cost  
- Latency  
- Hallucination control  
- Safety features  
- Model updates  

### 7.2 Compliance Strategy
Developers must detail:
- What PHI is processed  
- What PHI is masked  
- What logs contain  
- What assurance mechanisms prevent unsafe advice  

### 7.3 RAG Strategy
Explain:
- Chunking  
- Embeddings  
- Filters  
- Clinical guideline alignment  

### 7.4 Multi-Agent Coordination Plan
Explain:
- Controller vs peer-to-peer  
- Memory strategy  
- Message schema  

### 7.5 Tools/APIs Design
Define:
- Schemas  
- Expected data validation  
- Error/timeout patterns  

### 7.6 Frontend-Backend Interaction
Include:
- Diagram  
- Authentication (if any)  
- State-handling  

### 7.7 Database Selection Justification

### 7.8 Docker Setup Explanation

---

# 8. Expected Best Practices

### 8.1 Python Engineering
- Modular structure  
- Pydantic models  
- dotenv  
- Clear error handling  
- Structured logging  

### 8.2 Agent Best Practices
- Deterministic prompts  
- Evidence-grounded generation  
- Rewriting vague queries  
- Preventing leakage of entire documents  
- Strict safety wrappers  

### 8.3 RAG Best Practices
- Avoiding hallucinations  
- Using citations  
- Metadata-driven retrieval  
- Chunk deduplication  

### 8.4 Compliance Best Practices
- Minimize output PHI  
- Filter risky statements  
- “Assistive only” language  
- Inline safety disclaimers  

### 8.5 Frontend Best Practices
- No direct model calls  
- Safety warnings  
- Clear indication of data usage  

### 8.6 Docker Best Practices
- Multi-stage builds  
- .dockerignore usage  
- No secrets baked into images  

---

# 9. Evaluation Rubric

| Category | Weight | Description |
|---------|--------|-------------|
| **Compliance & Safety** | 20% | PHI minimization, safe outputs, audit logs |
| **Multi-Agent Workflow** | 20% | Coordination, message schemas, memory, accuracy |
| **RAG Pipeline** | 15% | Retrieval quality, grounding, citations |
| **Backend/API Engineering** | 15% | Tool schemas, validation, modularity |
| **Frontend Integration** | 10% | Clarity, UX, structured visualization |
| **Observability** | 10% | Logs, traces, correlation IDs |
| **Dockerization** | 5% | Multi-service setup |
| **Documentation** | 5% | Architecture, decisions, diagrams |

---

# 10. Future Enhancements (Developer Must Propose at least 5)

Suggested enhancements:
1. On-device PHI encryption (AES 256)  
2. Radiology-image agent (using vision models)  
3. Medication safety checker (non-diagnostic)  
4. Multi-step clinical pathway reasoning  
5. Auto-clustering of historical notes  
6. Real-time compliance dashboard  
7. Clinical chatbot for patient education  
8. Integration with FHIR/HL7  

---

# 11. Submission Requirements

- FastAPI backend  
- Streamlit/Gradio UI  
- Multi-agent implementation  
- RAG indexing + search  
- Docker Compose  
- Compliance Report  
- Observability Dashboard (App Insights)  
- Architecture Document  
- README  

---

# End of Document
