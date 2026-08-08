# PropAI — Design Spec

**Date:** 2026-08-08
**Status:** Approved for implementation
**Client:** Prolov (property agency)
**Market:** Jawa Barat
**Scope:** 8 days, 2 of 4 agents
**Source docs:** `AGENTS.md` (concrete spec), `PLANNING.md` (narrative spec)

---

## 1. Scope Decision

`AGENTS.md` budgets **12 days for 4 agents without landing pages**. The requested budget is **8 days with landing pages added**. That gap is resolved by cutting agent count, not by compressing quality.

### In scope

| Component | Source |
|---|---|
| Content Creator Agent | AGENTS.md §1, PLANNING.md §1 |
| Sales & Lead Coordinator Agent | AGENTS.md §2, PLANNING.md §2 |
| Landing pages + per-agent short links | PLANNING.md line 19 |
| Auth + RBAC (3 roles) | AGENTS.md RBAC matrix |
| Bilingual output (Indonesian + English) | Decision, this session |

### Deferred (explicitly not built)

- **Agency Manager Agent** — analytics, Google Calendar sync, weekly reports
- **Data Ingestion Agent** — `acehome.co.id` scraper. **Stale target:** the market moved
  to Jawa Barat on 2026-08-08, so this Aceh-specific source no longer matches. A West Java
  listing source must be chosen when that phase is specced.
- `surveys` table (belongs to Agency Manager; no dead migration shipped)
- Custom domains per agent, A/B testing of copy variants

Each deferred item is a later spec → plan → implementation cycle.

---

## 2. Resolved Conflicts Between Source Docs

| Axis | PLANNING.md | AGENTS.md | Resolution |
|---|---|---|---|
| Timeline | — | 12 days | **8 days**, 2 agents |
| Agent count | 3 | 4 | **2** |
| Vector store | Pinecone or Weaviate | Postgres only | **pgvector** (see §6) |
| Orchestrator | LangChain | LangGraph | **LangGraph**, scoped to qualification only |
| Integration layer | Langflow | Langflow | **Dropped** — explicit Python is more legible at 2 agents |
| Landing pages | line 19 | absent | **In scope**; schema extended |

### Model IDs

`PLANNING.md` specifies `GPT 5.6` and `GPT Image 2`. Both verified real as of 2026-08-08:

- `gpt-5.6` — alias routing to `gpt-5.6-sol`. Tiers: `sol` ($5/$30 per 1M), `terra`, `luna` ($0.20/$1.20). 1.05M context, Feb 2026 cutoff.
- `gpt-image-2` — current image model. `dall-e-3` was **removed from the API on 2026-05-12**.

**Cost lever** (AGENTS.md constraint #2): `luna` for high-volume 24/7 chat, `sol`/`terra` for low-volume content generation.

Sources: [All models](https://developers.openai.com/api/docs/models/all), [GPT Image 2](https://developers.openai.com/api/docs/models/gpt-image-2), [Deprecations](https://developers.openai.com/api/docs/deprecations)

---

## 3. Architecture

Microservices on **Podman** (4.9.3 rootless, `podman-compose` 1.0.6, buildah — all verified working; Docker absent). Six containers.

```
postgres        pgvector/pgvector:pg16
                relational tables + vector embeddings

redis           redis:7-alpine
                job queue + response cache (constraint #2)

api             FastAPI  :8000
                auth/RBAC, listings CRUD, PUBLIC landing pages,
                /r/{code} redirect, contact endpoint, channel webhooks

content-agent   worker (no port)
                consumes content jobs: label -> copy (ID+EN)
                -> SEO -> staging -> landing page

sales-agent     FastAPI  :8001
                LangGraph qualification, pgvector RAG,
                scoring, sentiment, handoff

dashboard       Streamlit  :8501
                agent console, chat widget, job status polling
```

### Repo layout

```
propai/
  compose.yaml
  packages/propai_core/      # models, schemas, db, config, provider interfaces
  services/api/
  services/content_agent/
  services/sales_agent/
  services/dashboard/
  seeds/                     # synthetic Jawa Barat listings + ID/EN documents
  tests/
```

`propai_core` is an installed local package. Services do **not** import across each other's boundaries.

Dependency management: **uv** (installed; substantially faster than pip in image builds).

> `REPOLAYOUT.md` at repo root contains an earlier draft of this section and the data model. This spec supersedes it.

### Provider interfaces

`LLMProvider`, `ImageProvider`, `EmbeddingProvider`, `ChannelProvider`, `VectorStore` — each with a real implementation and a fixture-backed fake selected by env.

Consequence: **the full test suite runs offline with no proxy token.** This is what keeps the build moving when the proxy is down or rate-limited.

### LLM access

Via OpenAI-compatible proxy (AgentRouter / 9router). Canonical env names — **not** `OPENAI_API_KEY`:

```
LLM_BASE_URL
LLM_API_TOKEN
LLM_MODEL
```

The `openai` Python SDK accepts `base_url` directly, so the proxy is a drop-in.

**Capability probes at startup.** Many OpenAI-compatible proxies forward only `/chat/completions`. The system probes `/images/generations` and `/embeddings` on boot and degrades rather than crashing (see §8).

---

## 4. Data Model

`AGENTS.md` specifies 4 tables. That schema cannot express bilingual content, landing pages, shortlink attribution, RAG chunks, or async jobs. Extended to **13 tables** — a deliberate, flagged deviation.

| Table | Purpose | Deviation from AGENTS.md |
|---|---|---|
| `users` | `id`, `email`, `password_hash`, `full_name`, `role` | + auth fields |
| `properties` | + `owner_id`, `specs` jsonb (bedrooms, land/building area) | + ownership |
| `property_photos` | labels jsonb, `is_staged` flag | new |
| `content_assets` | **`lang` column** — one row per language | new |
| `landing_pages` | `slug`, `lang`, `published_at` (nullable) | new |
| `short_links` | `code` → `agent_id` + `property_id` | new |
| `link_clicks` | hashed IP, user agent, referrer | new |
| `leads` | + **`source_short_link_id`**, `score`, `status` | phone now nullable |
| `conversations` | + **`short_link_id`**, sentiment, `handoff_requested` | new |
| `messages` | role, content, per-turn sentiment | replaces `leads.chat_log` |
| `documents` | RAG corpus source | new |
| `document_chunks` | content + `vector` embedding | new |
| `jobs` | kind, payload, status, attempts, error | new |

### Notable schema decisions

- **`content_assets.lang`** — bilingual falls out of a query, not a schema fork.
- **`leads.chat_log` → `messages` table** — a text blob cannot support per-turn sentiment or handoff detection.
- **`leads.phone` nullable** — web-chat leads begin anonymous (see §7). Contradicts AGENTS.md's implicit assumption that phone is known at creation.
- **`leads.status`** — `anonymous` → `contacted` → `qualified` / `cold`.
- **`surveys` omitted** — deferred with Agency Manager.

---

## 5. Content Creator Agent

### Pipeline

Agent selects property → uploads photos → Generate. Writes a `jobs` row, pushes to Redis. `content-agent` runs five stages, **checkpointing per stage** so a stage-4 failure does not discard stages 1–3.

1. **Photo labeling** → `property_photos.labels`
2. **Copy** — AIDA, per target demographic → `content_assets`
3. **SEO** — keywords + meta description → `content_assets`
4. **Virtual staging** — `gpt-image-2`; skipped if capability probe failed
5. **Landing page + shortlink** → `landing_pages`, `short_links`

### Key decisions

**AIDA as structured output.** `gpt-5.6` returns a Pydantic-validated object — `attention` (headline), `interest` (body), `desire` (highlights list), `action` (CTA) — not free text requiring regex extraction. Renderable into any channel template; testable field-by-field.

**One bilingual call, not two.** A single structured call returns both `id` and `en` variants together. Cheaper, and keeps the two semantically aligned — sequential calls drift, producing an English page that claims something the Indonesian one does not.

**Vision via the proxy, not Google.** No Google Cloud credential is available and the setup is proxy-only. `gpt-5.6` is multimodal, so labeling uses the same `LLM_BASE_URL`. Google Vision remains an optional adapter behind `LLMProvider`.

**Caching** (constraint #2): Redis key over `hash(property_specs + demographic + lang + prompt_version)`. Regenerating an unchanged listing costs nothing. `prompt_version` in the key means editing a prompt correctly invalidates cache rather than serving stale copy.

**Target demographics**: enum — `millennial`, `young_family`, `investor`.

### Human-in-the-loop (constraint #1)

Generated content is a **draft**. `landing_pages.published_at` stays null until an agent reviews and approves in the dashboard. Nothing the AI writes is publicly reachable until a human publishes it.

This is also what makes bilingual output safe: the agent catches a bad Indonesian translation before a buyer sees it.

---

## 6. Vector Store: pgvector over Weaviate

Weaviate was considered and rejected for this scope. Reasons, in order of weight:

1. **Bilingual hybrid retrieval.** Postgres ships an `indonesian` text-search config (verified present alongside `english`). This allows dense vector search **and** Indonesian-stemmed BM25 in one SQL query, joined directly to `properties`. Weaviate's BM25 has no Indonesian stemmer — lexical recall degrades on exactly the domain terms that matter (`sertifikat`, `HGB`, `KPR`).

   **Measured limitation (2026-08-08).** The stemmer handles verb affixes correctly —
   `dijual` and `menjual` both reduce to `jual` — but it over-strips some nouns:
   `perumahan` reduces to `rumah`, which does **not** unify with `rumah`. So Indonesian
   FTS is not a substitute for semantic search on noun morphology. This strengthens
   rather than weakens the hybrid design: the dense-vector half covers precisely the
   recall gap the lexical half leaves. Lexical-only retrieval would miss these matches.

2. **RBAC is the security argument.** The matrix scopes leads per agent. With pgvector that is `WHERE owner_id = :user` in the same query as the vector search. With Weaviate, authorization logic is duplicated into Weaviate metadata filters that must stay in sync with Postgres truth. Duplicated authorization across two stores is how leads leak between agents.

3. **No distributed deletes.** Chunks and properties commit in one transaction. With Weaviate, deleting a property is a two-store operation with no transaction — orphaned vectors serving stale answers.

4. **Topology cost.** Weaviate is a 7th container, ~1–2GB RAM, its own volume. The corpus is ~4 seed documents — a few hundred chunks. pgvector HNSW is comfortable into the millions.

**Weaviate remains a drop-in.** The `VectorStore` interface means outgrowing pgvector requires a new adapter, not a rewrite. Revisit at multi-agency tenancy or millions of listings.

---

## 7. Sales & Lead Coordinator Agent

### Entry point — the seam between the two agents

The landing page's **Contact Agent button is the Sales agent's front door.** Content Creator's output feeds Sales agent's input directly. There is no separate lead-capture form.

`POST /p/{slug}/contact` → creates an anonymous `leads` row + a `conversations` row → returns a session token → opens chat. The buyer types first; the bot responds.

**Lead identity is progressive.** A web-chat lead starts with `name` and `phone` null — only a click is known. Qualification enriches turn by turn.

### Channel layer

`ChannelProvider` with two adapters, converging on one conversation engine:

- **Web chat (primary)** — dashboard/landing page → `sales-agent:8001`. AI answers 24/7. Works today with no Twilio.
- **`wa.me` escape hatch (secondary)** — deep link to the agent's own WhatsApp with the property code prefilled. **Requires no Twilio, no Meta verification, no API.** Lands with a human, so no AI reply. Offered on the landing page and at bot handoff.
- **Twilio WhatsApp (later)** — `POST /webhooks/whatsapp` on `api`, normalized to the same internal message shape. Upgrades the WhatsApp path to bot-answered without changing the page.

### Attribution

Chain: **shortlink → click → conversation → lead → agent.**

Survives differently per channel:

- **Web chat** — `ref` in URL → session → `conversations.short_link_id`.
- **WhatsApp** — cookies cannot cross into WhatsApp. The code is embedded in the prefilled message text (`"Halo, saya tertarik dengan Rumah Lamprit (kode: A7K2M9)"`) and parsed off the first inbound message. **Without this, every WhatsApp lead loses agent attribution.**

Short codes: 7-char base62, collision-checked on insert.

This chain is what makes the RBAC rule "Freelance Agent sees own leads" meaningful — a lead from a freelancer's post is provably theirs.

### Qualification graph

LangGraph earns its place here: qualification is genuinely stateful — slots fill across turns while the buyer interleaves questions with answers.

Nodes: `classify_intent` → `retrieve` → `answer` → `qualify` → `score` → `handoff?`
Postgres checkpointer, so conversations survive worker restarts.

**Slots**: budget, payment method (cash / KPR), urgency, preferred location, property type.

The graph asks for the highest-value missing slot rather than interrogating in fixed order, and **always answers the buyer's actual question first** — a bot that ignores *"berapa harganya?"* to ask about budget gets abandoned.

### Scoring is deterministic

The LLM extracts slot **values**; a plain Python function computes the score. Weighted rubric over budget-fits-inventory, payment method, urgency, engagement depth, explicit viewing requests → 0–100, bucketed hot/warm/cold.

Rationale: an LLM-assigned score is not reproducible. The same lead scoring 72 then 61 destroys agent trust in the ranking and the feature dies. A deterministic function is auditable, unit-testable, and tunable without touching a prompt.

### Grounding — the liability surface

A chatbot that invents a price or improvises about `sertifikat` status creates legal exposure for the agency, in writing, to a buyer. Three hard rules:

1. **Prices and specs never come from the model.** Injected from the `properties` row as structured facts. The LLM phrases them; it never recalls them.
2. **Legal and financing answers must cite a retrieved chunk.** If hybrid retrieval returns nothing above the similarity threshold, the bot says it does not know and offers a human. It does not fill the gap. **This refusal path is a tested feature, not a fallback.**
3. **No legal or financial advice.** It explains what documents *are* and what the brochure says. It does not opine on whether a specific purchase is safe, and says so plainly when asked.

### Handoff triggers

Explicit request · negative-sentiment streak · score crossing hot threshold · retrieval failure on a legal question.

Each writes `conversations.handoff_requested` and surfaces in the dashboard queue — constraint #1, humans close the deal.

### Language mirroring

The bot detects the buyer's language per message and replies in it. Indonesian and English buyers both get native-feeling conversation from one corpus.

### PII (constraint #3)

Leads are phone numbers and names — the most sensitive data in the system.

- Message bodies and lead contact details **stay out of application logs** (IDs only).
- Click IPs stored **hashed**.
- RBAC scoping on `leads` enforced **in the query layer**, not the UI — a crafted API call cannot read another agent's pipeline.
- Unauthorized lead access returns **404, not 403** (403 confirms the record exists).

---

## 8. Failure Handling

| Failure | Behavior |
|---|---|
| Proxy down / 5xx | Job retries with backoff (3 attempts), stage checkpoints preserved, error shown in dashboard |
| `/images/generations` unsupported | Startup probe disables stage 4; copy/SEO/landing page still ship |
| `/embeddings` unsupported | Falls back to local `sentence-transformers` (~400MB, 384-dim); RAG degrades to BM25-only if both fail |
| Malformed LLM JSON | One repair-prompt retry, then fail job with raw response stored |
| Retrieval empty | Refuse + offer handoff — designed path, not an error |
| Redis down | API stays up; generation queues rejected with clear message; public pages unaffected |

**Public landing pages and `/r/{code}` redirects depend only on Postgres.** If every AI service is down, published pages still serve and still capture leads.

---

## 9. Testing

Five areas get real tests rather than coverage theater:

1. **RBAC matrix** — table-driven across 4 modules × 3 roles from AGENTS.md, asserted at the query layer.
2. **Attribution chain** — click → conversation → lead → agent, end-to-end. Most likely to break silently, least likely to be noticed.
3. **Scoring** — pure function, unit tests over fixed slot inputs. Same input, same score.
4. **Grounding refusal** — retrieval below threshold must produce "I don't know + offer human".
5. **Bilingual structure** — both `id` and `en` present, AIDA fields non-empty, no language bleed.

All run offline against fixture-backed fakes.

---

## 10. Seed Data

Synthetic, generated during Phase 1:

- **~15 Jawa Barat listings** — Bandung / Bekasi / Bogor / Depok areas, IDR pricing, plausible specs.
- **3–4 Indonesian property documents** — `sertifikat`/HGB explainer, KPR financing FAQ, developer brochure. These form the RAG corpus.

Real data swaps in whenever available; no scraper dependency.

---

## 11. Eight-Day Plan

Conventional-commit style, one commit per feature, each day ending on a working state.

| Day | Phase | Ships | Commits |
|---|---|---|---|
| 1 | Foundation | `.gitignore` **first**, compose (6 services), pgvector, migrations, `propai_core` | ~6 |
| 2 | Auth + data | Password auth, RBAC query layer, listings CRUD, synthetic Jawa Barat seed | ~6 |
| 3 | Content I | Provider interfaces + probes, bilingual AIDA copy, SEO, Redis cache | ~6 |
| 4 | Content II | Photo labeling, `gpt-image-2` staging, job queue, dashboard review/approve | ~7 |
| 5 | Landing pages | Jinja2 pages, shortlink codes, `/r/{code}` + click tracking, contact button + `wa.me` | ~7 |
| 6 | RAG | Doc ingest, chunking, embeddings, hybrid ID/EN retrieval, grounding rules | ~6 |
| 7 | Sales agent | LangGraph qualification, scoring, sentiment, handoff, live web chat | ~8 |
| 8 | Integration | Twilio adapter, dashboard lead pipeline, README + demo script, hardening | ~7 |

**~53 commits total. Day 5 is the integration keystone** — after it a buyer can click a link and land on a real page, the first genuinely demoable moment.

### Schedule risks

- **LangGraph + checkpointer wiring** is the likeliest overrun. If it slips, the qualification flow ships as explicit Python rather than losing the feature.
- **If the proxy forwards neither `/images/generations` nor `/embeddings`**, days 4 and 6 shrink to fallbacks. The app still completes, with less visual polish.

---

## 12. Security Baseline

- `.gitignore` covering `.env` is **commit #1**, before any other file exists. `.env` was verified unignored at spec time; the token would otherwise enter history on first `git add`.
- `.env.example` committed with key names and empty values.
- Passwords hashed (bcrypt/argon2), never logged.
- RBAC enforced in the query layer.
- PII kept out of logs; click IPs hashed.
- No secrets in image layers — injected at runtime via compose env.

---

## 13. Open Items

| Item | Needed by | Fallback if absent |
|---|---|---|
| `LLM_BASE_URL` / `LLM_API_TOKEN` / `LLM_MODEL` populated in `.env` | Day 3 | Fixture fakes; suite still passes, no real generation |
| Proxy `/images/generations` support | Day 4 | Stage 4 disabled by probe |
| Proxy `/embeddings` support | Day 6 | Local `sentence-transformers`, then BM25-only |
| Twilio credentials + public tunnel | Day 8 | `wa.me` escape hatch; Twilio adapter shipped untested against live API |
| `acehome.co.id` ToS review | Deferred phase | Scraper not built in this cycle |

**Note on `acehome.co.id`:** the site serves **no `robots.txt`** (404 verified). Nothing to violate, but no explicit crawl permission either. Its Terms of Service must be reviewed before the Data Ingestion agent is built — AGENTS.md constraint #4 assumes a `robots.txt` that does not exist.
