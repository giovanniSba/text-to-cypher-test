import argparse
import json
import requests
from typing import Any, List, Dict

def call_database_api(endpoint: str, query: str) -> List[Dict[str, Any]]:
    """Executes a CoGQL query on the proprietary database."""
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }
    response = requests.post(endpoint, data=query.encode('utf-8'), headers=headers)
    response.raise_for_status()
    return response.json()

def generate_ground_truth(input_path: str, output_path: str, db_endpoint: str) -> None:
    """Runs the first expected query for each test case to generate the ground truth file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    ground_truth = []
    total_cases = len(dataset)

    print(f"Generating ground truth for {total_cases} cases against {db_endpoint}...")

    for idx, test_case in enumerate(dataset, 1):
        case_id = test_case["id"]
        queries = test_case.get("queries", [])
        
        print(f"  [{idx}/{total_cases}] {case_id} -> ", end="", flush=True)

        if not queries:
            print("❌ No queries available")
            ground_truth.append({"id": case_id, "expected": []})
            continue

        # Use the first valid query to get the ground truth records
        target_query = queries[0]

        try:
            records = call_database_api(db_endpoint, target_query)
            ground_truth.append({
                "id": case_id,
                "expected": records
            })
            print(f"✅ Fetched {len(records)} records")
        except Exception as e:
            print(f"💥 Error: {e}")
            ground_truth.append({
                "id": case_id,
                "expected": []
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=4)
    
    print(f"\nGround truth successfully saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ground truth from test queries.")
    parser.add_argument("-i", "--input", required=True, help="Path to the test dataset JSON file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output ground truth JSON file")
    parser.add_argument("--api_db", required=True, help="Database API endpoint URL")
    
    args = parser.parse_args()
    generate_ground_truth(args.input, args.output, args.api_db)