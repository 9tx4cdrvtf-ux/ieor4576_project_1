"""Golden-example evals: judge the bot's output against reference answers."""

from conftest import get_review, judge_with_golden
from golden_dataset import GOLDEN_DATASET

GOLDEN_EXAMPLES = [
    {
        "name": f"Example {item['id']}",
        "input": item["input"],
        "reference": item["expected"],
    }
    for item in GOLDEN_DATASET
]

def test_golden_examples():
    """Each bot response should score >= 6/10 against its golden reference."""
    print()
    ratings = []
    for example in GOLDEN_EXAMPLES:
        response = get_review(example["input"])
        rating = judge_with_golden(
            prompt=example["input"],
            reference=example["reference"],
            response=response,
        )
        ratings.append(rating)
        print(f"  {example['name']}: {rating}/10")
        assert rating >= 6, (
            f"[{example['name']}] Rating {rating}/10 — response: {response[:200]}"
        )
    print(f"  average: {sum(ratings) / len(ratings):.1f}/10")
