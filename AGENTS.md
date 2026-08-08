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
- **24/7 Response:** Answering general inquiries (price, location, facilities) via WhatsApp.
- **Qualification:** Performing lead scoring (budget, payment method, urgency).
- **CRM:** Structuring and storing contact data into the database.
- **Human-in-the-Loop:** Providing follow-up recommendations based on conversation sentiment.

---

## 3. Agency Manager Agent
The operational brain that monitors business health and manages field logistics.

### Roles & Responsibilities
- **Analytics:** Monitoring ad performance and recommending marketing budget allocation.
- **Logistics:** Synchronizing property survey visits between agents and buyers via calendar.
- **Reporting:** Generating weekly reports on new leads, conversion status, and agent effectiveness.

---

## 4. Data Ingestion Agent (Scraping)
This agent enriches the property inventory by automatically fetching listings from external platforms to supplement manual input.

### Roles & Responsibilities
- **Scraping:** Regularly scanning `acehome.co.id` to detect new listings or price changes.
- **Extraction:** Capturing building specifications, location coordinates, and market prices.
- **Normalization:** Cleaning and standardizing data formats before inserting them into the central database.

---

## Tech Stack & Infrastructure
For our 12-day MVP development, we utilize the following stack:

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.12+ |
| **Backend** | FastAPI (High Performance) |
| **Frontend** | Streamlit (Rapid Dashboard) |
| **Orchestrator** | LangGraph (Stateful Multi-Agent) |
| **Database** | PostgreSQL (Relational Data) |
| **Scraping** | BeautifulSoup4 / Playwright |
| **Integration** | Langflow |

---

## Role-Based Access Control (RBAC)

| Module | Super Admin | Property Agent | Freelance Agent |
| :--- | :---: | :---: | :---: |
| **Manage Listings** | CRUD All | CRUD Own | Read Only |
| **Scraping Data** | Full Access | No Access | No Access |
| **Leads Data** | All Data | Own Leads | Own Leads |
| **Agency Analytics** | Full Access | Own Stats | No Access |

---

## Database Schema (MVP)

### 1. Users
- `id`, `email`, `role` (admin, agent, freelance)
### 2. Properties
- `id`, `title`, `price`, `description`, `location`, `status`, `source_url` (origin: acehome.co.id)
### 3. Leads
- `id`, `name`, `phone`, `interest_level`, `last_contacted`, `chat_log`
### 4. Surveys
- `id`, `property_id`, `lead_id`, `appointment_time`, `status`

---

## Project Timeline (12 Days)

| Phase | Duration | Main Focus |
| :--- | :---: | :--- |
| **Phase 1: Initialization** | Days 1-3 | DB, RBAC, Scraping Setup (acehome) |
| **Phase 2: Content Creator** | Days 4-6 | Prompt Engineering, Vision API Integration |
| **Phase 3: Sales Coordinator** | Days 7-9 | Chatbot, RAG setup, WA Integration |
| **Phase 4: Manager & Demo** | Days 10-12 | Calendar, Reporting, Final Polish |

---

## Constraints
1. **Human-in-the-Loop:** AI acts as a co-pilot; final decisions remain with humans.
2. **API Rate Limits:** Caching used for cost optimization.
3. **Data Privacy:** Basic encryption implemented for PII data.
4. **Scraping Ethics:** Strict adherence to `robots.txt` on target sites (`acehome.co.id`).
