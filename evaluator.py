from typing import List, Dict, Any

def check_exact_match(generated: str, expected_queries: List[str]) -> bool:
    """Returns True if the generated query exactly matches any of the expected queries."""
    if not generated:
        return False
    gen_clean = generated.strip()
    return any(gen_clean == exp.strip() for exp in expected_queries)

def _canonicalize_dict(d: Dict[str, Any]) -> frozenset:
    """Converts a dictionary into a hashable set of items for comparison."""
    return frozenset(d.items())

def calculate_score(actual_records: List[Dict[str, Any]], expected_records: List[Dict[str, Any]]) -> float:
    """Calculates intersection percentage between actual and expected records."""
    if not expected_records:
        return 1.0 if not actual_records else 0.0
        
    expected_set = set(_canonicalize_dict(d) for d in expected_records)
    actual_set = set(_canonicalize_dict(d) for d in actual_records)
    
    intersection = expected_set.intersection(actual_set)
    return len(intersection) / len(expected_set)