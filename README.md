# Texas Hold'em Hub

A professional Texas Hold'em rules and beginner strategy assistant. 

This assistant provides:
- Clear explanations of poker mechanics
- Definitions of terminology
- Beginner-friendly strategic reasoning
- Structured analysis of example hands

It focuses strictly on educational poker theory and does **not** provide gambling advice, betting recommendations, or real-time outcome predictions.

**Live URL:** [https://texas-holdem-hub-64874377471.us-central1.run.app/](https://texas-holdem-hub-64874377471.us-central1.run.app/)

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- Google Cloud Project with Vertex AI API enabled

## Setup & Running Locally

1. **Clone the repository** and navigate to the project folder.
2. **Create a `.env` file** in the root directory:

```env
VERTEXAI_PROJECT=your-project-id
VERTEXAI_LOCATION=us-central1
```
3. **Install dependencies and run:**

```bash
uv run python app.py
```
4. **Access the Hub**: Open http://localhost:8000 in your browser.

## API Reference

- `GET /` - Serves the chatbot UI
- `POST /chat` - Send rule questions or hand descriptions, returns professional analysis
- `POST /clear` - Clear session history

## Evals

The `evals/` directory contains pytest-based evaluations using Model-as-a-Judge:

- `test_golden.py` - Judge bot responses against golden reference answers
- `test_rubric.py` - Judge bot responses against weighted rubric criteria
- `test_refusal_detection.py` - Verify the bot correctly triggers the "escape hatch" for out-of-scope topics

```bash
uv run pytest evals/ -sv
```

Note: Evals require active Google Cloud credentials and will incur small API usage costs.