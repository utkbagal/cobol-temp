
# **MACIS – Multi‑Agent Claims Intelligence System**

MACIS is an **enterprise-grade Multi‑Agent AI system** built for the **Insurance domain**, enabling automated claim intake, document processing, metadata extraction, compliance evaluation, and intelligent summarization using RAG (Retrieval‑Augmented Generation).  
This project implements major components of the *Insurance Developer Capstone* specification.

---

# 🧠 **1. Key Features**

### **Multi-Agent Architecture**
- **Intake Agent** – Extracts key claim metadata  
- **Compliance Agent** – Performs compliance rule checks  
- **Summarization Agent** – Produces structured summaries  
- Agents run sequentially under an orchestrator

### **RAG Pipeline**
- PDF/TXT/DOCX ingestion  
- Chunking + embeddings  
- Vector retrieval using **ChromaDB**  
- Metadata-based filtering  

### **Backend – FastAPI**
- Document upload  
- Embedding  
- Retrieval  
- Multi‑agent inference API  

### **Frontend – Streamlit**
- Document upload interface  
- Chat-like agent response viewer  
- Summary & metadata display  

### **Dockerized Deployment**
- Multi‑service Docker Compose setup  
- Streamlit UI + FastAPI backend  

---

# 📂 **2. Project Structure**

```
macis/
│   README.md
│   requirements.txt
│
├── app/
│   ├── main.py
│   ├── api/
│   ├── agents/
│   ├── rag/
│   ├── db/
│   ├── utils/
│   ├── tools/
│   ├── config/
│   └── .env
│
└── frontend/
    ├── chat_ui.py
    └── ui.py
```

---

# ⚙ **3. Installation & Setup**

## **3.1 Prerequisites**

- Python 3.10+
- Streamlit
- FastAPI + Uvicorn
- Docker (optional)
- OpenAI API Key

---

# 🧩 **3.2 Local Setup**

### **1️⃣ Clone the repository**
```bash
git clone <your-repo-url>
cd macis
```

### **2️⃣ Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### **3️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Configure environment variables**
Create file: `app/.env`

```
OPENAI_API_KEY=your-key-here
VECTOR_DB_PATH=./vector_store
MODEL_NAME=gpt-4.1-mini
EMBED_MODEL=text-embedding-3-large
```

### **5️⃣ Start backend**
```bash
cd app
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### **6️⃣ Start UI**
```bash
cd frontend
streamlit run ui.py
```

UI runs at: `http://localhost:8501`

---

# 🐳 **4. Docker Deployment**

From the project root:

```bash
docker-compose up --build
```

This automatically builds:
- FastAPI backend  
- Streamlit UI  
- ChromaDB volume  

---

# 🧱 **5. Architecture**

### **5.1 Multi-Agent Flow**

```
User Uploads Document
        |
        v
  [Preprocessing]
        |
        v
  [RAG Chunking + Embedding]
        |
        v
  ┌───────────────────────────┐
  │      Intake Agent         │
  └───────────────────────────┘
        |
        v
  ┌───────────────────────────┐
  │     Compliance Agent      │
  └───────────────────────────┘
        |
        v
  ┌───────────────────────────┐
  │   Summarization Agent     │
  └───────────────────────────┘
        |
        v
   Final Output to UI
```

### **5.2 RAG Components**
Located in `/app/rag/`

- `chunker.py` – splits text into semantically meaningful chunks  
- `embedder.py` – wraps OpenAI embeddings  
- `vector_store.py` – ChromaDB integration  
- `retriever.py` – search ranks and returns relevant chunks  

---

# 🔌 **6. API Endpoints**

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/upload` | POST | Upload claim documents |
| `/embed` | POST | Convert document to embeddings |
| `/retrieve` | POST | Retrieve relevant chunks |
| `/process` | POST | Runs full multi-agent pipeline |
| `/health` | GET | Health status |

---

# 🖥 **7. Frontend Usage**

1. Open Streamlit at:  
   `http://localhost:8501`
2. Upload a document  
3. System processes text & runs agents  
4. View:
   - Extracted metadata  
   - Compliance notes  
   - Summary  

---

# 🔮 **8. Future Enhancements**

- Risk Triage Agent (Low/Medium/High classification)  
- Policy lookup API integration  
- Claim-status update API  
- Azure App Insights observability  
- Retry/backoff logic for tools  
- Hybrid retrieval (keyword + vector)  
- Fraud signal detection  
- Multi-turn memory  

---

# 📝 **9. Limitations**

- No dedicated relational/NoSQL DB  
- Observability layer not implemented  
- Risk triage missing  
- No microservice separation for policy APIs  
- Limited input validation  

---

# © **10. License**

MIT License (or customize as required)

---

# 🙌 **Acknowledgments**

This project was built from the Capstone specification:  
**Insurance Developer Capstone – Multi-Agent Claims Intelligence System (MACIS)**

