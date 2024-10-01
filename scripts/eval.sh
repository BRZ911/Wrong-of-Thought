
DATASET='gsm'


python src/analyze.py \
  --mode analyze  \
  --plan_data outputs/${DATASET}/plan/DEMO_plan_0_end.jsonl \
  --eot_data outputs/${DATASET}/check_answer_eot/first/DEMO_check_answer_eot_0_end.jsonl \
  --pot_data outputs/${DATASET}/check_answer_pot/first/DEMO_check_answer_pot_0_end.jsonl \
  --eot_data_2 outputs/${DATASET}/check_answer_eot/second/DEMO_check_answer_eot_0_end.jsonl \
  --pot_data_2 outputs/${DATASET}/check_answer_pot/second/DEMO_check_answer_pot_0_end.jsonl \
  --cot_data outputs/${DATASET}/cot_error/DEMO_cot_error_0_end.jsonl

