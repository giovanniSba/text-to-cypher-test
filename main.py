import argparse
import json
import itertools
import os
from datetime import datetime
from typing import List, Dict, Any
from api_client import call_translation_api, call_database_api
from evaluator import check_exact_match, calculate_score
from reporter import generate_report

def load_json(filepath: str) -> Any:
    """Loads a JSON file and returns its content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_tests(args: argparse.Namespace) -> None:
    gt_data = load_json(args.ground_truth)
    gt_lookup = {item["id"]: item.get("expected", []) for item in gt_data}

    if args.vary_main_only:
        er_id = args.er_model_ids[0]
        hypo_id = args.hypo_model_ids[0]
        model_combinations = [(mod_id, er_id, hypo_id) for mod_id in args.model_ids]
    else:
        model_combinations = list(itertools.product(
            args.model_ids, args.er_model_ids, args.hypo_model_ids
        ))

    all_results = []

    for test_file in args.test_files:
        test_dataset = load_json(test_file)

        for mod_id, er_id, hypo_id in model_combinations:
            models_config = {
                "model_id": mod_id,
                "er_model_id": er_id,
                "hypo_model_id": hypo_id
            }
            
            print(f"\nTesting {test_file} with config: {models_config}")
            
            total_cases = len(test_dataset)
            for idx, test_case in enumerate(test_dataset, 1):
                case_id = test_case["id"]
                nl_query = test_case["text"]
                expected_queries = test_case["queries"]
                expected_records = gt_lookup.get(case_id, [])

                print(f"  [{idx}/{total_cases}] {case_id} -> ", end="", flush=True)

                result_entry = {
                    "case_id": case_id,
                    "file": test_file,
                    "models": models_config,
                    "nl_query": nl_query,
                    "hypothetical_query": "",
                    "extracted_entities": [],
                    "exact_match": False,
                    "score": 0.0,
                    "elapsed_time": 0,
                    "error": None
                }

                try:
                    trans_res = call_translation_api(args.api_trans, nl_query, models_config)
                    result_entry["elapsed_time"] = trans_res.get("total_elapsed_time", 0)
                    
                    # Extract new requested fields
                    result_entry["hypothetical_query"] = trans_res.get("hypothetical_query", "")
                    result_entry["extracted_entities"] = trans_res.get("retrieved_entities", {}).get("extracted_entities", [])
                    
                    last_attempt = trans_res.get("last_attempt", {})
                    generated_query = last_attempt.get("generated_cogql", {}).get("query", "")
                    result_entry["generated_query"] = generated_query

                    if check_exact_match(generated_query, expected_queries):
                        result_entry["exact_match"] = True
                        result_entry["score"] = 1.0
                        print("✅ Exact Match")
                    else:
                        if generated_query:
                            db_res = call_database_api(args.api_db, generated_query)
                            score = calculate_score(db_res, expected_records)
                            result_entry["score"] = score
                            print(f"⚠️  DB Match (Score: {score:.2f})")
                        else:
                            result_entry["score"] = 0.0
                            print("❌ No query generated")

                except Exception as e:
                    result_entry["error"] = str(e)
                    print(f"💥 Error: {e}")
                
                all_results.append(result_entry)

    base_name, ext = os.path.splitext(args.output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_output = f"{base_name}_{timestamp}{ext}"

    generate_report(all_results, timestamped_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test platform for Text-to-CoGQL.")
    parser.add_argument("--test_files", nargs='+', required=True, help="List of test JSON files")
    parser.add_argument("--ground_truth", required=True, help="JSON file with expected database records")
    parser.add_argument("--api_trans", required=True, help="Translation API endpoint URL")
    parser.add_argument("--api_db", required=True, help="Database API endpoint URL")
    
    parser.add_argument("--model_ids", nargs='+', default=["gemma4:26b"], help="List of main model IDs")
    parser.add_argument("--er_model_ids", nargs='+', default=["gemma4:12b"], help="List of ER model IDs")
    parser.add_argument("--hypo_model_ids", nargs='+', default=["hermes3:8b"], help="List of Hypo model IDs")
    
    parser.add_argument("--vary_main_only", action="store_true", help="Test only model_ids, using the first element of er_model_ids and hypo_model_ids")
    
    parser.add_argument("--output", default="test_report.json", help="Base path to output report file (timestamp will be appended)")

    args = parser.parse_args()
    run_tests(args)