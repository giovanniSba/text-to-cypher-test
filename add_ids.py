import json
import argparse
import os

def inject_ids_to_dataset(input_path: str, output_path: str) -> None:
    """Reads the dataset, injects a unique ID per record, and saves the output."""
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Reconstruct dict to place 'id' at the top of each record
    enriched_dataset = [
        {"id": f"test_{i:04d}", **record} 
        for i, record in enumerate(dataset, start=1)
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_dataset, f, indent=4)
    
    print(f"Processed {len(enriched_dataset)} records. Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject unique IDs into the training dataset.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input JSON file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output JSON file")
    
    args = parser.parse_args()
    inject_ids_to_dataset(args.input, args.output)
