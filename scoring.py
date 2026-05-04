from typing import Dict, List, Optional
from collections import defaultdict
from difflib import SequenceMatcher

from models import ProteinReport, BrandAEOScore

RANK_POINTS = {1: 3, 2: 2, 3: 1}
FUZZY_THRESHOLD = 0.65


def _fuzzy_match(name: str, known_brands: List[str]) -> str:
    """Maps a model-returned brand name to the closest known canonical brand name."""
    name_lower = name.lower()

    # Substring match first: "Optimum Nutrition Gold Standard" → "Optimum Nutrition"
    for known in known_brands:
        if known.lower() in name_lower or name_lower in known.lower():
            return known

    # Fallback: fuzzy ratio
    best_match = None
    best_ratio = FUZZY_THRESHOLD
    for known in known_brands:
        ratio = SequenceMatcher(None, name_lower, known.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = known

    return best_match if best_match else name


def compute_aeo_scores(
    model_results: Dict[str, ProteinReport],
    known_brands: Optional[List[str]] = None,
) -> List[BrandAEOScore]:
    num_models = len(model_results)
    max_possible = num_models * RANK_POINTS[1]

    brand_data = defaultdict(lambda: {"points": 0, "appearances": 0, "models": []})

    for model_name, report in model_results.items():
        for rec in report.recommendations:
            raw_name = rec.brand_name.strip()
            canonical = _fuzzy_match(raw_name, known_brands) if known_brands else raw_name
            key = canonical.lower()
            brand_data[key]["points"] += RANK_POINTS.get(rec.rank, 0)
            brand_data[key]["appearances"] += 1
            brand_data[key]["models"].append(model_name)
            brand_data[key]["display_name"] = canonical

    scores = []
    for _, data in brand_data.items():
        scores.append(BrandAEOScore(
            brand_name=data["display_name"],
            total_points=data["points"],
            model_appearances=data["appearances"],
            models_that_ranked=data["models"],
            visibility_pct=round((data["points"] / max_possible) * 100, 1),
        ))

    return sorted(scores, key=lambda x: x.total_points, reverse=True)