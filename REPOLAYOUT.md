# PropAI — Repo Layout & Data Model

> Quick reference. The authoritative spec is
> [`docs/superpowers/specs/2026-08-08-propai-design.md`](docs/superpowers/specs/2026-08-08-propai-design.md).
> Where the two disagree, the spec wins.

## Repo layout

Monorepo, one Containerfile per Python service, shared code as an installed local package so services don't import across each other's boundaries:

```
propai/
  compose.yaml                 # podman-compose, 6 services
  packages/propai_core/        # shared: models, schemas, db, config, providers
  services/api/                # FastAPI :8000
  services/content_agent/      # worker, no port
  services/sales_agent/        # FastAPI :8001
  services/dashboard/          # Streamlit :8501
  seeds/                       # synthetic Jawa Barat listings + ID/EN docs
  tests/
```

`propai_core` holds the SQLAlchemy models, Pydantic schemas, and **five** provider interfaces:

| Interface | Real implementation | Fake |
|---|---|---|
| `LLMProvider` | `gpt-5.6` via `LLM_BASE_URL` | recorded fixtures |
| `ImageProvider` | `gpt-image-2` | recorded fixtures |
| `EmbeddingProvider` | proxy `/embeddings` → local `sentence-transformers` | deterministic vectors |
| `ChannelProvider` | web chat · `wa.me` · Twilio | in-memory transport |
| `VectorStore` | pgvector | in-memory |

Each has a real implementation and a fixture-backed fake selected by env. That's what makes the whole system testable with no proxy token and no network — and it's how the `gpt-image-2` capability probe degrades gracefully if the proxy only forwards `/chat/completions`.

`uv` for dependency management (already installed, and far faster in an image build than pip).

## Services

| Service | Port | Responsibility |
|---|---|---|
| `postgres` | 5432 | `pgvector/pgvector:pg16` — relational tables + embeddings |
| `redis` | 6379 | job queue + response cache |
| `api` | 8000 | auth/RBAC, listings CRUD, public landing pages, `/r/{code}`, contact endpoint, webhooks |
| `content-agent` | — | worker: label → copy (ID+EN) → SEO → staging → landing page |
| `sales-agent` | 8001 | LangGraph qualification, RAG, scoring, sentiment, handoff |
| `dashboard` | 8501 | Streamlit console, chat widget, job status polling |

## Data model

`AGENTS.md` specifies 4 tables. That schema can't express bilingual content, landing pages, shortlink attribution, RAG chunks, or async jobs — so it extends to 13. A flagged deviation, not a silent one:

| Table | Purpose |
|---|---|
| `users` | `+ password_hash`, `full_name`. Roles per the RBAC matrix |
| `properties` | `+ owner_id`, `specs` jsonb (bedrooms, land/building area) |
| `property_photos` | vision labels, staged-vs-original flag |
| `content_assets` | **`lang` column** — one row per language. Bilingual falls out of a query, not a schema fork |
| `landing_pages` | `slug`, `lang`, `published_at` — null until a human approves |
| `short_links` | `code` → agent + property. The per-agent unique link |
| `link_clicks` | click tracking, hashed IP |
| `leads` | **`source_short_link_id`** — this FK is the entire attribution story. `phone` nullable |
| `conversations` | **`short_link_id`**, sentiment, `handoff_requested` |
| `messages` | role, content, per-turn sentiment. Replaces `leads.chat_log` |
| `documents` | RAG corpus source |
| `document_chunks` | content + `vector` embedding |
| `jobs` | async work: kind, payload, status, attempts, error |

`surveys` is **omitted** — it belongs to the deferred Agency Manager agent, and shipping a dead migration is worse than shipping none.

## Attribution chain

The one path worth memorising, because it's what makes "Freelance Agent sees own leads" enforceable:

```
short_links.code
  -> link_clicks          (GET /r/{code}, hashed IP)
  -> conversations        (POST /p/{slug}/contact, carries ref)
  -> leads                (source_short_link_id)
  -> users                (agent_id)
```
