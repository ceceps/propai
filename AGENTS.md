# AI Agent Architecture: PropAI

This document details the technical specifications and functional roles of the multi-agent system powering the **PropAI** platform. This system is designed to automate the property marketing cycle, from generating creative assets to proactive Customer Relationship Management (CRM).

---

## 1. Content Creator Agent
This agent acts as a creative engine, transforming technical property data into persuasive and visually appealing marketing materials.

### Roles & Responsibilities
- **Copywriting:** Drafting ad descriptions using the AIDA (*Attention, Interest, Desire, Action*) framework.
- **Visual Assets:** Generating suggestions for interior design or virtual staging based on raw unit photos.
- **SEO:** Optimizing keywords to ensure property listings are discoverable on search engines.
- **Adaptation:** Tailoring content tone based on the target demographic (e.g., millennials, investors, young families).

---

## 2. Sales & Lead Coordinator Agent
The frontline for buyer interactions, ensuring every inquiry is answered instantly and leads are qualified before being handed off to human agents.

### Roles & Responsibilities
- **24/7 Response:** Answering general inquiries (price, location, facilities) via Web Chat & WhatsApp.
- **Qualification:** Performing lead scoring (budget, payment method, urgency).
- **CRM:** Structuring and storing contact data into the database.
- **Human-in-the-Loop:** Providing follow-up recommendations based on conversation sentiment.

---

## 3. Agency Manager Agent (Deferred)
The operational brain that monitors business health and manages field logistics.

### Roles & Responsibilities
- **Analytics:** Monitoring ad performance and recommending marketing budget allocation.
- **Logistics:** Synchronizing property survey visits between agents and buyers via calendar.
- **Reporting:** Generating weekly reports on new leads, conversion status, and agent effectiveness.

---

## 4. Data Ingestion Agent (Scraping) (Deferred)
This agent enriches the property inventory by automatically fetching listings from external platforms to supplement manual input.

### Roles & Responsibilities
- **Scraping:** Regularly scanning external platforms to detect new listings or price changes.
- **Extraction:** Capturing building specifications, location coordinates, and market prices.
- **Normalization:** Cleaning and standardizing data formats before inserting them into the central database.

---

## Tech Stack & Infrastructure

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.12+ |
| **Backend** | FastAPI (High Performance) |
| **Frontend** | React 19 + Vite + TypeScript + Bun (build) |
| **Orchestrator** | LangGraph (Stateful Multi-Agent Qualification) |
| **Database** | PostgreSQL 15 + pgvector (Relational + Vector) |
| **Caching/Queue** | Redis (TCP localhost:6379) |
| **Scraping** | BeautifulSoup4 / Playwright (Deferred) |
| **Package Manager** | uv (Python), Bun (Frontend) |
| **Process Manager** | PM2 / systemd (Production) |

---

## Role-Based Access Control (RBAC)

| Module | Super Admin | Property Agent | Freelance Agent |
| :--- | :---: | :---: | :---: |
| **Manage Listings** | CRUD All | CRUD Own | Read Only |
| **Scraping Data** | Full Access | No Access | No Access |
| **Leads Data** | All Data | Own Leads | Own Leads |
| **Agency Analytics** | Full Access | Own Stats | No Access |

---

## Database Schema (Implemented)

### 1. Users
- `id`, `email`, `password_hash`, `full_name`, `role` (admin, agent, freelance), `whatsapp_number`, `is_active`

### 2. Properties
- `id`, `title`, `description`, `price`, `location`, `status`, `source_url`, `owner_id`, `specs` (JSONB)

### 3. Properties Photos
- `id`, `property_id`, `path`, `labels` (JSONB), `is_staged`, `sort_order`

### 4. Content Assets (Bilingual AIDA + SEO)
- `id`, `property_id`, `lang` (id/en), `demographic`, `attention`, `interest`, `desire` (JSONB), `action`, `seo_keywords`, `seo_meta_description`

### 5. Landing Pages
- `id`, `property_id`, `content_asset_id`, `slug`, `lang`, `published_at`, `published_by_id`

### 6. Short Links (Attribution)
- `id`, `code`, `property_id`, `agent_id`, `landing_page_id`, `campaign`

### 7. Link Clicks
- `id`, `short_link_id`, `ip_hash`, `user_agent`, `referrer`

### 8. Leads
- `id`, `name`, `phone`, `email`, `status`, `score`, `score_breakdown`, `short_link_id`, `property_id`, `assigned_agent_id`

### 9. Conversations
- `id`, `lead_id`, `channel`, `lang`, `thread_id`

### 10. Messages
- `id`, `conversation_id`, `role`, `content`, `citations`, `model_used`, `token_cost`

### 11. Documents (RAG Corpus)
- `id`, `title`, `lang`, `source_path`, `content_sha256`, `property_id`

### 12. Document Chunks (pgvector)
- `id`, `document_id`, `chunk_index`, `content`, `embedding` (vector(1536)), `meta`

### 13. Jobs (Async Pipeline)
- `id`, `kind`, `payload`, `status`, `attempts`, `error`, `started_at`, `finished_at`

---

## Project Status (Current)

| Phase | Status | Notes |
| :--- | :---: | :--- |
| **Phase 1: Foundation** | ✅ Complete | DB, RBAC, Auth, Migrations (13 tables) |
| **Phase 2: Content Creator** | ✅ Complete | AIDA bilingual, SEO, Job pipeline, pgvector RAG |
| **Phase 3: Sales Coordinator** | ✅ Complete | LangGraph qualification, Web Chat, Deterministic Scoring |
| **Phase 4: Frontend Migration** | ✅ Complete | React + Vite + Bun + Tailwind (replaced Streamlit) |
| **Phase 5: Local Deployment** | ✅ Complete | Native Python/PostgreSQL/Redis (No Docker) |

---

## Constraints
1. **Human-in-the-Loop:** AI acts as a co-pilot; final decisions remain with humans.
2. **API Rate Limits:** Caching used for cost optimization.
3. **Data Privacy:** Basic encryption implemented for PII data.
4. **Scraping Ethics:** Strict adherence to `robots.txt` on target sites.

---

## Local Development Environment (Non-Docker)
```bash
# Services
PostgreSQL 15: localhost:5432 (DB: propai, User: postgres)
Redis: localhost:6379
FastAPI: localhost:8000
Frontend Dev: localhost:5173 (Vite)

# Commands
uvicorn propai_api.main:app --host 0.0.0.0 --port 8000 --reload
rq worker --url redis://localhost:6379/0 default
cd services/frontend && bun run dev
```

---

## Deferred Items (Post-MVP)
- Agency Manager Agent (Analytics, Calendar, Reports)
- Data Ingestion Agent (External scraping)
- Twilio WhatsApp Integration
- Custom domains per agent, A/B testing