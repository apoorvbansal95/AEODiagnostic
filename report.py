from typing import Dict, List

from models import BrandAEOScore

W = 62


def print_single_report(query: str, model_results: Dict, aeo_scores: List[BrandAEOScore]):
    print("=" * W)
    print("AEO DIAGNOSTIC REPORT — Single Query")
    print(f"Query: {query}")
    print("=" * W)

    for model_name, report in model_results.items():
        print(f"\n{model_name} Rankings:")
        for rec in report.recommendations:
            print(f"  {rec.rank}. {rec.brand_name} — {rec.reasoning}")

    print(f"\n{'—' * W}")
    print(f"{'BRAND AEO VISIBILITY SCORES':^{W}}")
    print(f"{'—' * W}")
    print(f"{'Brand':<28} {'Points':>6}  {'Models':>6}  {'Visibility':>10}")
    print(f"{'—' * W}")
    for s in aeo_scores:
        consensus = " [CONSENSUS]" if s.model_appearances == len(model_results) else ""
        print(f"{s.brand_name:<28} {s.total_points:>6}  {s.model_appearances:>6}  {s.visibility_pct:>9}%{consensus}")
    print("=" * W)


def print_multi_query_report(results: Dict):
    total_queries = results["total_queries"]
    print(f"\n{'=' * W}")
    print(f"{'MULTI-QUERY AEO AGGREGATE REPORT':^{W}}")
    print(f"Total Queries Tested: {total_queries}")
    print(f"{'=' * W}")
    print(f"\n{'Brand':<28} {'Points':>7}  {'Queries':>7}  {'Stability':>10}")
    print(f"{'—' * W}")

    for b in results["aggregated"]:
        stable_tag = " [STABLE]" if b["stability_pct"] == 100.0 else ""
        fluky_tag = " [FLUKY]" if b["query_appearances"] == 1 and total_queries > 1 else ""
        tag = stable_tag or fluky_tag
        print(
            f"{b['brand_name']:<28} {b['total_points']:>7}  "
            f"{b['query_appearances']:>7}  {b['stability_pct']:>9}%{tag}"
        )

    print(f"\n{'—' * W}")
    print("STABLE  = brand appeared in every query variation")
    print("FLUKY   = brand appeared in only 1 query")
    print("=" * W)


def print_brand_report(results: Dict):
    target = results["target"]
    competitors = results["competitors"]
    total_queries = results["total_queries"]
    max_pts = results["max_total_points"]

    print(f"\n{'=' * W}")
    print(f"{'BRAND AEO DIAGNOSTIC REPORT':^{W}}")
    print(f"{'=' * W}")

    # --- Target brand ---
    print(f"\nTARGET BRAND: {target['brand_name']}")
    print(f"{'—' * W}")
    print(f"  Total Points      : {target['total_points']} / {max_pts}")
    print(f"  Overall Visibility: {target['overall_visibility_pct']}%")
    print(f"  Queries Found In  : {target['query_appearances']} / {total_queries}")
    print(f"  Stability         : {target['stability_pct']}%")
    if target["queries_missed"]:
        print(f"  AEO Opportunities (not mentioned in):")
        for q in target["queries_missed"]:
            print(f"    - {q}")
    else:
        print(f"  AEO Opportunities : None — present in all queries!")

    # --- Competitor comparison ---
    print(f"\n{'COMPETITOR ANALYSIS':^{W}}")
    print(f"{'—' * W}")
    print(f"{'Brand':<24} {'Points':>6}  {'Visibility':>10}  {'Gap':>8}  {'Queries':>7}")
    print(f"{'—' * W}")

    for comp in competitors:
        gap = comp["gap_vs_target"]
        gap_str = f"+{gap}" if gap > 0 else str(gap)
        status = " AHEAD" if gap > 0 else (" TIED" if gap == 0 else " BEHIND")
        print(
            f"{comp['brand_name']:<24} {comp['total_points']:>6}  "
            f"{comp['overall_visibility_pct']:>9}%  {gap_str:>8}  "
            f"{comp['query_appearances']:>7}{status}"
        )

    # --- Summary ---
    ahead = sum(1 for c in competitors if c["gap_vs_target"] > 0)
    behind = sum(1 for c in competitors if c["gap_vs_target"] < 0)
    print(f"\n{'—' * W}")
    print(f"  {target['brand_name']} is AHEAD of {ahead} and BEHIND {behind} competitor(s).")
    print(f"{'=' * W}")