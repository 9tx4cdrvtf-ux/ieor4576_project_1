# Texas Hold'em Hub

A professional Texas Hold'em rules and beginner strategy assistant. This bot provides clear, factual guidance on poker mechanics, terminology, and foundational strategy — helping players understand the game without providing gambling advice or real-time winnings predictions.

## Prerequisites

You need Google Cloud set up with Vertex AI. See the **Google Cloud & Vertex AI Setup Guide**.

Create a `.env` file in this directory:

```
VERTEXAI_PROJECT=your-project-id
VERTEXAI_LOCATION=us-central1
```

## Running

```bash
uv run python app.py
```

Open http://localhost:8000 in your browser.

## API

- `GET /` - Serves the chatbot UI
- `POST /chat` - Send rule questions or hand descriptions, returns professional analysis
- `POST /clear` - Clear session history
