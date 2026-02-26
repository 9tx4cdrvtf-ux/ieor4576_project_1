"""Golden-example evals: judge the bot's output against reference answers."""

from collections import defaultdict
from conftest import get_review, judge_with_golden
from golden_dataset import GOLDEN_DATASET

GOLDEN_EXAMPLES = [
    {
        "name": f"Example {item['id']}",
        "category": item["category"],
        "input": item["input"],
        "reference": item["expected"],
    }
    for item in GOLDEN_DATASET
]

def test_golden_examples():
    """Each bot response should score >= 6/10 against its golden reference."""
    print()
    ratings = []
    stats = defaultdict(lambda: {"total": 0, "passed": 0})

    for example in GOLDEN_EXAMPLES:
        response = get_review(example["input"])
        rating = judge_with_golden(
            prompt=example["input"],
            reference=example["reference"],
            response=response,
        )
        ratings.append(rating)

        cat = example["category"]
        stats[cat]["total"] += 1
        if rating >= 6:
            stats[cat]["passed"] += 1

        # print(f"  {example['name']} ({cat}): {rating}/10")
        assert rating >= 6, (
            f"[{example['name']}] Rating {rating}/10 — response: {response[:200]}"
        )

    print(f"  overall average: {sum(ratings) / len(ratings):.1f}/10")
    for cat, s in stats.items():
        rate = s["passed"] / s["total"]
        print(f"  [{cat}] pass rate: {s['passed']}/{s['total']} ({rate:.0%})")
