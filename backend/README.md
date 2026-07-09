# AI Knowledge Inbox — Backend

FastAPI backend for a minimal RAG-powered knowledge inbox. Save notes/URLs,
ask questions, get answers grounded in your saved content with cited sources.

**Stack:** FastAPI · Google Gemini 2.5 Flash(LLM) · Google `text-embedding-001`
(embeddings) · Pinecone (vector store) · SQLite (system of record)

---

## Project layout

```
app/
├── main.py                      # FastAPI app, middleware, exception handlers, startup
├── config.py                    # env-driven settings (pydantic-settings)
├── database.py                  # SQLite connection + schema
├── schemas.py                   # request/response models + validation
├── logging_config.py            # structured JSON logging
├── routers/
│   ├── ingest.py                # POST /ingest
│   ├── items.py                 # GET /items
│   └── query.py                 # POST /query
└── services/
    ├── chunking.py              # chunking strategy
    ├── scraper.py               # URL fetch + text extraction
    ├── embeddings.py            # Google text-embedding-004
    ├── vectorstore.py           # Pinecone wrapper
    ├── llm.py                   # Gemini 2.5 Flash Lite generation
    ├── ingestion_service.py     # orchestrates ingest pipeline
    └── query_service.py         # orchestrates RAG query pipeline

```

## Setup

```bash
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

cp .env.example .env
# then fill in GOOGLE_API_KEY and PINECONE_API_KEY in .env
```

Get keys:

- Google API key: https://aistudio.google.com/apikey
- Pinecone API key: https://app.pinecone.io

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## API

### `POST /ingest`

```json
// text note
{ "source_type": "text", "content": "Some note text...", "title": "optional" }

// URL (fetched server-side)
{ "source_type": "url", "url": "https://example.com/article", "title": "optional" }
```

→ `201` `{ id, source_type, title, chunk_count, created_at }`
→ `422` if content/url missing, blank, or the URL fails to fetch
→ `502` if embedding or vector upsert fails

### `GET /items`

→ `200` `{ items: [{ id, source_type, title, source_url, chunk_count, created_at, content_preview }], count }`

### `POST /query`

```json
{ "question": "What did the article say about X?", "top_k": 5 }
```

→ `200` `{ answer, sources: [{ item_id, title, chunk_index, chunk_text, score }], retrieved_chunk_count }`
→ `502` if embedding/vector-search/LLM step fails

---
