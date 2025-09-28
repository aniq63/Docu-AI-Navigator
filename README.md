<h1 align="center">📘 DocuAI Navigator</h1>
<p align="center">
  <b>AI-powered workspace for document management, team collaboration, and smart project planning</b>  
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-2C3E50?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/VectorDB-FF6F00?style=for-the-badge&logo=databricks&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Generation-FF4088?style=for-the-badge&logo=openai&logoColor=white" />
</p>

---

## 🚀 Overview
**DocuAI Navigator** is an AI-powered workspace that helps companies and teams manage documents, collaborate effectively, and generate intelligent project plans.  
It combines **FastAPI**, **LangChain**, and **Vector Databases** to deliver smart workflows and seamless AI assistance.

From **document uploads** to **team/project creation** and **AI-generated roadmaps**, DocuAI Navigator transforms raw documents into actionable insights.

---

## ✨ Features
- 📂 **Document Management** – Upload, validate, and organize project/company docs  
- 🤖 **AI-Powered Search & Chat** – Ask questions directly to your documents using RAG (Retrieval-Augmented Generation)  
- 🏗 **Smart Project Planning** – Auto-generate detailed project plans based on domain, team size, and tools  
- 👥 **Team Collaboration** – Create teams and projects with secure authentication  
- 📊 **Modern Dashboard** – Clean, intuitive UI for company, team, and project management  

---

## 🛠 Tech Stack
- **Backend:** FastAPI, SQLAlchemy ORM
- **Database:** PostgreSQL  
- **AI & NLP:** LangChain, LLMs (for RAG, name extraction, and planning)  
- **Vector Store:** Chroma / FAISS (configurable)  
- **Frontend:** HTML, CSS, Vanilla JS (extendable)  

---

## 📂 Repository Structure
```

Docu-AI-Navigator/
├── Routers/         # API routes for company, team, and project
├── Services/        # AI/LLM services, PDF validators, vector store logic
├── docs/            # 📖 Project documentation (setup, usage, workflows, diagrams)
├── frontend/        # HTML/CSS/JS for dashboards and UI
├── database.py      # DB connection setup
├── main.py          # FastAPI entry point
├── models.py        # Database models (SQLAlchemy ORM)
├── schemas.py       # Pydantic schemas
├── requirements.txt # Dependencies
└── .env             # Environment variables (ignored in .gitignore)

````

📖 **Full documentation is available in the [`docs/`](./docs) folder.**  
It includes system workflow diagrams, API usage, and project details.

---

## ⚡ Quick Start

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/aniq63/Docu-AI-Navigator.git
cd Docu-AI-Navigator
````

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_secret_key
```

### 4️⃣ Run the Application

```bash
uvicorn main:app --reload
```

Visit 👉 `http://127.0.0.1:8000/docs` for Swagger API docs.

---

## 📖 Documentation

The **`docs/` folder** contains:

* System Architecture & Workflow diagrams
* Detailed explanation of RAG pipeline (Parent/Child chunks, embeddings, retriever)
* API Endpoints & Usage
* Project planning examples

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a pull request.

---

## 📧 Contact

For feedback, support, or collaboration:
📩 **aniqramzan5758@gmail.com**

---

<p align="center">
  &copy; 2025 DocuAI Navigator — Smarter, Faster, AI-driven Collaboration
</p>
