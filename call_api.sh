#!/bin/bash
uv run main.py \
  --test_files cogql-test-queries-wids.json \
  --ground_truth ground_truth.json \
  --api_trans "http://localhost:8000/translate" \
  --api_db "http://localhost:8082/nems/query/3" \
  --model_ids gemma4:26b\
  --er_model_ids gemma4:12b \
  --hypo_model_ids hermes3:8b \
  --vary_main_only
