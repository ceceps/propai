Repo layout
   
  Monorepo, one Containerfile per Python service, shared code as an
  installed local package so services don't import across each other's
  boundaries:
  
  propai/ 
    compose.yaml                 # podman-compose, 6 services
    packages/propai_core/        # shared: models, schemas, db, config,
  providers
    services/api/                # FastAPI :8000
    services/content_agent/      # worker, no port
    services/sales_agent/        # FastAPI :8001
    services/dashboard/          # Streamlit :8501
    seeds/                       # synthetic Aceh listings + ID/EN docs
    tests/
  
  propai_core holds the SQLAlchemy models, Pydantic schemas, and the
  three provider interfaces (LLMProvider, ImageProvider,
  ChannelProvider). Each provider has a real implementation and a
  fixture-backed fake, selected by env. That's what makes the whole
  system testable with no proxy token and no network — and it's how the
  gpt-image-2 capability probe degrades gracefully if your proxy only
  forwards /chat/completions.
  
  uv for dependency management (already installed, and far faster in an
  image build than pip).

  Data model

  AGENTS.md specifies 4 tables. That schema can't express bilingual
  content, landing pages, shortlink attribution, RAG chunks, or async
  jobs — so I'm extending it to 13. Flagging that as a real deviation,
  not a silent one:
  
  ┌────────────────────┬───────────────────────────────────────────┐
  │       Table        │                  Purpose                  │
  ├────────────────────┼───────────────────────────────────────────┤
  │ users              │ + password_hash, full_name. Roles per the │
  │                    │  RBAC matrix                              │
  ├────────────────────┼───────────────────────────────────────────┤
  │ properties         │ + owner_id, specs jsonb (bedrooms,        │
  │                    │ land/building area)                       │
  ├────────────────────┼───────────────────────────────────────────┤
  │ property_photos    │ Vision labels, staged-vs-original flag    │
  ├────────────────────┼───────────────────────────────────────────┤
  │                    │ lang column — one row per language.       │
  │ content_assets     │ Bilingual falls out of a query, not a     │
  │                    │ schema fork                               │
  ├────────────────────┼───────────────────────────────────────────┤
  │ landing_pages      │ slug, lang, published state               │
  ├────────────────────┼───────────────────────────────────────────┤
  │ short_links        │ slug → agent + property. The per-agent    │
  │                    │ unique link                               │
  ├────────────────────┼───────────────────────────────────────────┤
  │ link_clicks        │ click tracking, hashed IP                 │
  ├────────────────────┼───────────────────────────────────────────┤
  │ leads              │ + source_short_link_id — this FK is the   │
  │                    │ entire attribution story                  │
  ├────────────────────┼───────────────────────────────────────────┤
  │ conversations /    │ chat state, sentiment, handoff flag       │
  ├────────────────────┼───────────────────────────────────────────┤
  │ documents /        │ RAG corpus + vector embeddings            │
  │ document_chunks    │                                           │
  ├────────────────────┼───────────────────────────────────────────┤
  │ jobs               │ async work, status, attempts, error       │
  └────────────────────┴───────────────────────────────────────────┘
