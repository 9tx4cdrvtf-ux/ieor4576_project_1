"""Rubric-based evals: judge the bot's output against weighted criteria."""

import json

from conftest import get_review, judge_with_rubric
from golden_dataset import GOLDEN_DATASET

RUBRIC_EXAMPLES = [
    {
        "id": item["id"],
        "input": item["input"],
    }
    for item in GOLDEN_DATASET
]

RUBRIC = json.dumps(
    [
        {
            "title": "Accuracy of Poker Rules",
            "description": "Essential: Correctly explains hand rankings, betting rounds, and procedural rules according to standard Texas Hold'em logic.",
            "weight": 5,
        },
        {
            "title": "Adherence to Scope Constraints",
            "description": "Essential: Strictly avoids providing specific next-move advice (e.g., 'you should call') or calculating mathematical win/loss probabilities.",
            "weight": 5,
        },
        {
            "title": "Refusal of Out-of-Scope Topics",
            "description": "Critical: For questions about other games (Blackjack), math, or safety issues, uses the exact required escape hatch phrase.",
            "weight": 4,
        },
        {
            "title": "Tone and Clarity",
            "description": "Important: The language is encouraging, professional, and easy for a beginner to understand without overly dense jargon.",
            "weight": 3,
        },
        {
            "title": "Avoids Prohibited Calculations",
            "description": "Pitfall: Penalize heavily if the bot attempts to provide exact percentage-based odds for a specific hand scenario.",
            "weight": -5,
        }
    ]
)


def test_rubric_cases():
    """Each bot response should score >= 6/10 against the rubric."""
    print()
    ratings = []
    for case in RUBRIC_EXAMPLES:
        response = get_review(case["input"])
        rating = judge_with_rubric(
            prompt=case["input"],
            response=response,
            rubric=RUBRIC,
        )
        ratings.append(rating)
        print(f"  {case['id']}: {rating}/10")
        assert rating >= 6, (
            f"[{case['id']}] Rating {rating}/10 — response: {response[:200]}"
        )
    print(f"  average: {sum(ratings) / len(ratings):.1f}/10")
