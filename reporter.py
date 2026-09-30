import json
from typing import List, Dict, Any

def generate_report(results: List[Dict[str, Any]], output_path: str) -> None:
    """Aggregates statistics and saves the detailed JSON report."""
    total_tests = len(results)
    exact_matches = sum(1 for r in results if r.get("exact_match", False))
    avg_score = sum(r.get("score", 0.0) for r in results) / total_tests if total_tests > 0 else 0
    avg_time = sum(r.get("elapsed_time", 0) for r in results) / total_tests if total_tests > 0 else 0

    report = {
        "summary": {
            "total_tests": total_tests,
            "exact_matches_count": exact_matches,
            "exact_match_rate": exact_matches / total_tests if total_tests > 0 else 0,
            "average_db_score": avg_score,
            "average_elapsed_time_ms": avg_time
        },
        "details": results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
    print(f"Report successfully saved to {output_path}")