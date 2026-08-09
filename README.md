# PropAI — Property Agency Marketing System
---

AI Builders Challenge with IBM Bob — August 2026  - Wildcard Case — 

---
<br/>

<p>
  <img src="https://img.shields.io/badge/status-active-green.svg"/>
  
  <img src="https://img.shields.io/badge/Python?style=for-the-badge&logo=Python&logoColor=white"/>
  
  <img src="https://img.shields.io/badge/IBM_Granite_AI-Powered-0062ff?style=for-the-badge&logo=ibm&logoColor=white"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Challenge-Wildcard-blueviolet?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Built_with-IBM_Bob-0062ff?style=for-the-badge&logo=ibm&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=flat-square"/>
</p>

<br/>

PropAI is a multi-agent system designed to automate the property marketing cycle, specifically tailored for the **Jawa Barat** (West Java) market. It transforms raw property data into persuasive marketing materials and handles lead qualification through AI-driven conversations.

---

## 📖 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [How to Run](#-how-to-run)
- [Contributing](#-contributing)

---

## 🚩 The Problem
Property agencies like **Prolov** face several challenges in the traditional sales cycle:
*   **Creative Bottleneck:** Manually drafting persuasive ad descriptions and preparing visual assets is time-consuming and inconsistent.
*   **Delayed Response:** Inquiries from prospective buyers often arrive outside business hours, leading to lost opportunities.
*   **Low Lead Quality:** Human agents spend significant time filtering through low-intent leads.
*   **Attribution Gaps:** Difficulty in proving which marketing channel or agent generated a specific lead.
*   **Bilingual Requirements:** The need to serve both local and international markets with consistent messaging.

---

## 🚀 The Solution
PropAI automates the frontline of property sales with a specialized AI agent workforce:

1.  **Content Creator Agent:** Automatically generates AIDA-optimized copy and SEO metadata in both Indonesian and English. It prepares virtual staging to make listings more attractive.
2.  **Sales & Lead Coordinator Agent:** Provides 24/7 instant response via web chat and WhatsApp. It qualifies leads through stateful conversations (gathering budget, urgency, payment method) and calculates deterministic lead scores.
3.  **Automated Landing Pages:** Every listing gets an AI-generated landing page with unique short links, ensuring perfect lead attribution.
4.  **Human-in-the-Loop:** AI acts as a co-pilot. Generated content remains in draft status until approved by a human, and complex inquiries are handed off to human agents.

---

## 🏗️ Architecture

The system is built on a microservices architecture using **Podman**, orchestrated by **LangGraph** for stateful qualification flows.

### Application Flow
1.  **Lead Capture**: User visits a property landing page via an agent-specific short link.
2.  **Interaction**: User clicks "Contact Agent", initiating a chat session handled by the **Sales Agent**.
3.  **Qualification**: The AI Agent uses **LangGraph** to strategically ask for buyer preferences (budget, urgency, etc.) while answering questions using **pgvector RAG**.
4.  **Deterministic Scoring**: Lead scores are calculated via Python logic based on extracted slots.
5.  **Human Handoff**: Hot leads or complex queries trigger a handoff to the human agent in the **Streamlit Dashboard**.

*   **Content Agent:** Pipeline-based worker that processes photo labeling, bilingual copy generation, and SEO optimization.
*   **Sales Agent:** FastAPI-based service managing conversational state, RAG retrieval, and deterministic scoring logic.
*   **Hybrid Retrieval:** Uses **pgvector** with Postgres, combining dense vector search for semantic matching with Indonesian-stemmed BM25 lexical search.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.12+ |
| **Backend** | FastAPI |
| **Orchestrator** | LangGraph, RQ |
| **LLMs** | GPT-5.6 (Text), GPT Image 2 |
| **Database** | Postgres + pgvector |
| **Frontend** | Streamlit |

---

## ⚙️ How to Run

### Prerequisites
- **Podman** & `podman-compose` (or Docker & `docker-compose`)
- Python 3.12+ (for running local tests)
- Nodejs 22.0.0 or latest

### Clone the Repo
```
git clone https://github.com/ceceps/propai
cd propai

```

### Running the Application

1. **Start Services** (Postgres, Redis, API, Dashboard, Worker):
   ```bash
   podman-compose up -d --build
   ```

2. **Run Database Migrations** (if not ran automatically):
   ```bash
   podman-compose run migrate
   ```

3. **Seed Initial Data**:
   ```bash
   podman exec -it propai_api_1 python -m seeds.run
   ```

4. **Access Applications**:
   - **API / Docs**: http://localhost:8000/docs
   - **Dashboard**: http://localhost:8501
   - **PostgreSQL**: `127.0.0.1:5433` (User: `propai`, Pass: `propai`, DB: `propai`)

5. **Run Tests**:
   ```bash
   pytest tests/
   ```

---

## 🤝 Contributing
For internal contributors, please check `AGENTS.md` and `PLANNING.md` in the `/docs` folder for detailed specifications before committing.
