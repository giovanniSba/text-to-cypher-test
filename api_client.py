import requests
from typing import Dict, Any, List

def call_translation_api(endpoint: str, text: str, models: Dict[str, str]) -> Dict[str, Any]:
    """Calls the translation API with dynamic model configurations."""
    # Remove empty model params
    params = {k: v for k, v in models.items() if v}
    
    payload = {
        "nl_query": text,
        "config": {
            "ontology_config": {"endpoint": "http://172.17.0.1:8081/synapsis/model/ontology?uri=http%3A%2F%2Fwww.okkam.it%2Fcogql", "format": "rdf"},
            "lang_syntax_endpoint": "http://172.17.0.1:8082/nems/query/language",
            "lang_description_endpoint": "http://172.17.0.1:8082/nems/query/language/description",
            "enable_schema_pruning": True,
            "neighbor_discovery": 0,
            "allow_data_properties_deduction": False,
            "allow_schema_expansion": True,
            "example_k_value": 5,
            "mmr_fetch_k": 20,
            "max_val_attempts": 3,
            "max_schema_expansion_requests": 3,
            "gliner_score_threshold": 0.6
        }
    }
    
    response = requests.post(endpoint, json=payload, params=params)
    response.raise_for_status()
    return response.json()

def call_database_api(endpoint: str, query: str) -> List[Dict[str, Any]]:
    """Executes the generated query on the proprietary database."""
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }
    # Payload is passed as raw string per user spec
    response = requests.post(endpoint, data=query.encode('utf-8'), headers=headers)
    response.raise_for_status()
    return response.json()
