import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from litellm import completion
from pydantic import BaseModel
import re
import os

load_dotenv()

# --- Config ---

MODEL = "vertex_ai/gemini-2.0-flash-lite"

SYSTEM_PROMPT = """\
<role>
You are a professional Texas Hold'em rules assistant designed for beginner players.
Your answers should be friendly, clear, and easy to understand, strictly following the official Texas Hold'em rules.
You primarily answer questions related to rules, gameplay, and procedures.
When a user explicitly asks for guidance, you may provide beginner-friendly general or specific strategic tips, such as hand selection, position awareness, or understanding aggression.
</role>

<scope>
Your allowed scope includes questions about:
1. The official rules of Texas Hold'em, including hand rankings, betting rounds, blinds, positions, and showdown procedures.
2. The sequence of play and how cards are dealt in each stage of the game.
3. Definitions of terminology used in Texas Hold'em for beginner players.
4. Procedural clarifications, such as when to act in betting rounds or what constitutes a valid action.
5. Situations for splitting pots or resolving ties according to the official rules.
6. Optional strategic guidance: when a user explicitly asks, provide beginner-friendly general or specific tips on gameplay, such as hand selection, position awareness, or understanding aggression.

Topics outside of these allowed scopes include, but are not limited to:
1. Sensitive personal or mental health topics (self-harm, suicidal thoughts, therapy advice).
2. Political, social, or current event discussions unrelated to poker.
3. General knowledge unrelated to poker (sports, movies, trivia, hobbies).
4. Financial, betting, or gambling advice beyond safe strategic guidance.
5. Probability calculations, odds, or next-move recommendations that require predicting outcomes or winnings.

If a question falls outside the allowed scope, respond with the escape hatch message.
</scope>


<output_constraints>
- Only answer questions within the allowed scope defined above. 
- Provide factual explanations for rules, hand rankings, betting rounds, blinds, positions, showdown procedures, or beginner-friendly strategy tips when asked.
- If the question is outside the scope of Texas Hold'em rules or strategy guidance, follow the escape hatch response.
- When no clear rules-related question is provided, ask the user to paste a specific Texas Hold'em rules question.
</output_constraints>

<escape_hatch>
If a question falls outside the allowed scope, respond with:
"I apologize, but I cannot assist with this specific topic. My expertise is strictly limited to Texas Hold'em rules and beginner strategy."
</escape_hatch>
"""


FEW_SHOT_EXAMPLES = [
    # In-domain rule explanation with kicker clarification
    # {
    #     "user": "What happens if two players have the same hand at showdown?",
    #     "assistant": (
    #         "If two players have the same hand ranking at showdown, the winner is determined "
    #         "by comparing the highest kicker cards (kicker means the highest card in a player's hand "
    #         "that is not part of the main hand combination) in order. "
    #         "If all relevant cards are identical, the pot is split evenly between the tied players."
    #     ),
    # },
    # In-domain basic rules explanation
    {
        "user": "What are the basic rules of Texas Hold'em?",
        "assistant": (
            "In Texas Hold'em, each player is first dealt two private hole cards. "
            "Five community cards are then dealt face-up on the table in stages, "
            "and players use any combination of their hole cards and the community cards "
            "to make the best five-card hand. Betting rounds determine the winner."
        ),
    },
    # Beginner-friendly strategic tip example (optional guidance)
    {
        "user": "Do you have any tips for playing my starting hands as a beginner?",
        "assistant": (
            "Sure! As a beginner, it's best to play strong starting hands, like high pairs (Aces, Kings) "
            "or suited connectors (like 10-J of the same suit), and avoid playing too many weak hands. "
            "Also, consider your position: being last to act in a betting round gives you more information "
            "about other players' actions, which is helpful when deciding whether to bet or fold."
        ),
    },
    # Out-of-scope refusal example
    {
        "user": "How much should I bet to maximize my winnings on this hand?",
        "assistant": (
           "I apologize, but I cannot assist with this specific topic. My expertise is strictly limited to Texas Hold'em rules and beginner strategy."
        ),
    },
]




def build_initial_messages() -> list[dict]:
    """Build the initial message list with system prompt and few-shot examples."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example["user"]})
        messages.append({"role": "assistant", "content": example["assistant"]})
    return messages


# --- LLM Call ---
def apply_python_backstop(text: str) -> str | None:
    """
    Perform a post-generation check (Backstop) on the content produced by the AI.
    If the content falls outside the allowed scope, return a specific fallback message; otherwise, return None.
    """
    text_lc = text.lower()

    # Safety Handling
    safety_keywords = [
    "suicide", "kill", "harm", "death", "bomb", "weapon", "terrorist", 
    "trump", "biden", "politics", "election", "democrat", "republican", "government",
    "financial", "stock", "win money", "make money", "betting advice", 
    "real money", "cash out", "gamble", "jackpot", "crypto", "bitcoin",
    "doctor", "medical", "depressed", "therapy", "medicine", "pill",
    "illegal", "hack", "steal", "drug", "porn"
    ]
    if any(key in text_lc for key in safety_keywords):
        return "I apologize, but I cannot assist with this specific topic. My expertise is strictly limited to Texas Hold'em rules and beginner strategy."

    # if the model already indicates it cannot answer 
    if "i'm not sure" in text_lc or "can only help" in text_lc:
        return None  # already reject

    return None


def generate_response(messages: list[dict]) -> str:
    try:
        response = completion(model=MODEL, messages=messages)
        content = response.choices[0].message.content

        # Python Backstop
        backstop_message = apply_python_backstop(content)
        if backstop_message:
            return backstop_message

        return content
    
    except Exception as e:
        return f"Something went wrong: {e}"


# def generate_response(messages: list[dict]) -> str:
#     """Generate a response using LiteLLM.

#     Args:
#         messages: List of message dicts with 'role' and 'content' keys.
#                   Example: [{"role": "user", "content": "Hello!"}]

#     Returns:
#         The assistant's response text.
#     """
#     try:
#         response = completion(model=MODEL, messages=messages)
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"Something went wrong: {e}"


# --- Session Management ---

# Each session stores a list of messages in OpenAI format:
# [
#     {"role": "system", "content": "..."},
#     {"role": "user", "content": "Hello!"},
#     {"role": "assistant", "content": "Hi there!"},
#     ...
# ]
sessions: dict[str, list[dict]] = {}


# --- FastAPI App ---

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
def index():
    return FileResponse("index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        # Start with the system prompt and few-shot examples
        sessions[session_id] = build_initial_messages()

    # Add user message to conversation
    sessions[session_id].append({"role": "user", "content": request.message})

    # Generate response
    response_text = generate_response(sessions[session_id])

    # Add assistant response to conversation history
    sessions[session_id].append({"role": "assistant", "content": response_text})

    return ChatResponse(response=response_text, session_id=session_id)


@app.post("/clear")
def clear(session_id: str | None = None):
    if session_id and session_id in sessions:
        del sessions[session_id]
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
