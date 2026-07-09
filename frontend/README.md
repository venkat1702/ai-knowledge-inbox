# AI Knowledge Inbox – Frontend

Frontend application for AI Knowledge Inbox, a Retrieval-Augmented Generation (RAG) system that allows users to ingest knowledge and ask questions against their personal knowledge base.

## Tech Stack

- React
- TypeScript
- Vite
- Tailwind CSS

## Project Structure

```text
src/
├── components/
│   ├── Ingest.tsx
│   └── Search.tsx
├── services/
│   └── api.ts
├── App.tsx
├── App.css
└── main.tsx
```

## Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Installation

Install dependencies:

```bash
npm ci
```

Start the development server:

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```
