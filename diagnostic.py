import time
from typing import List, Dict, Optional
from collections import defaultdict

from chains import ALL_CHAINS
from scoring import compute_aeo_scores, RANK_POINTS

MAX_RETRIES = 3


def _invoke_with_retry(chain, query_text: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return chain.invoke({"query": query_text})
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"    Retrying (attempt {attempt} failed: {type(e).__name__})")
            time.sleep(2 ** attempt)


def run_aeo_diagnostic(query_text: str, known_brands: Optional[List[str]] = None) -> tuple:
    print(f"  Querying models for: \"{query_text}\"")

    model_results = {
        name: _invoke_with_retry(chain, query_text)
        for name, chain in ALL_CHAINS.items()
    }

    aeo_scores = compute_aeo_scores(model_results, known_brands=known_brands)
    return model_results, aeo_scores


def run_multi_query_diagnostic(queries: List[str], known_brands: Optional[List[str]] = None) -> Dict:
    all_query_results = []
    brand_aggregate = defaultdict(lambda: {"points": 0, "query_appearances": 0, "query_list": []})

    print(f"\nRunning multi-query AEO diagnostic ({len(queries)} queries)...\n")

    for query in queries:
        model_results, aeo_scores = run_aeo_diagnostic(query, known_brands=known_brands)
        all_query_results.append({"query": query, "model_results": model_results, "scores": aeo_scores})

        for score in aeo_scores:
            key = score.brand_name.lower()
            brand_aggregate[key]["points"] += score.total_points
            brand_aggregate[key]["query_appearances"] += 1
            brand_aggregate[key]["query_list"].append(query)
            brand_aggregate[key]["display_name"] = score.brand_name

    aggregated = []
    for _, data in brand_aggregate.items():
        stability_pct = round((data["query_appearances"] / len(queries)) * 100, 1)
        aggregated.append({
            "brand_name": data["display_name"],
            "total_points": data["points"],
            "query_appearances": data["query_appearances"],
            "stability_pct": stability_pct,
            "queries_seen_in": data["query_list"],
        })

    aggregated.sort(key=lambda x: (x["total_points"], x["query_appearances"]), reverse=True)
    return {"per_query": all_query_results, "aggregated": aggregated, "total_queries": len(queries)}


def run_brand_diagnostic(target_brand: str, competitors: List[str], queries: List[str]) -> Dict:
    """
    Brand-centric AEO diagnostic. Measures target brand visibility vs. competitors
    across all queries and models, and surfaces missed queries as opportunities.
    """
    known_brands = [target_brand] + competitors
    num_models = len(ALL_CHAINS)
    max_points_per_query = num_models * RANK_POINTS[1]
    max_total = len(queries) * max_points_per_query

    raw = run_multi_query_diagnostic(queries, known_brands=known_brands)
    brand_map = {b["brand_name"].lower(): b for b in raw["aggregated"]}

    def _get_brand_stats(brand: str) -> Dict:
        data = brand_map.get(brand.lower(), {
            "brand_name": brand,
            "total_points": 0,
            "query_appearances": 0,
            "stability_pct": 0.0,
            "queries_seen_in": [],
        })
        missed = [q for q in queries if q not in data["queries_seen_in"]]
        return {
            "brand_name": brand,
            "total_points": data["total_points"],
            "query_appearances": data["query_appearances"],
            "stability_pct": data["stability_pct"],
            "overall_visibility_pct": round((data["total_points"] / max_total) * 100, 1) if max_total else 0.0,
            "queries_seen_in": data["queries_seen_in"],
            "queries_missed": missed,
        }

    target_stats = _get_brand_stats(target_brand)

    competitor_stats = []
    for comp in competitors:
        stats = _get_brand_stats(comp)
        stats["gap_vs_target"] = target_stats["total_points"] - stats["total_points"]
        competitor_stats.append(stats)

    competitor_stats.sort(key=lambda x: x["total_points"], reverse=True)

    return {
        "target": target_stats,
        "competitors": competitor_stats,
        "total_queries": len(queries),
        "max_total_points": max_total,
        "raw_results": raw,
    }