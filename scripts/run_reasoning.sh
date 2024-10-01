DATASET='algebra'
MODEL='gpt-4o-mini'

# plan
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode plan


python src/retrieve_data.py \
  --plan_data outputs/${DATASET}/plan/DEMO_plan_0_end.jsonl \
  --mode plan \
  --output_dir data/${DATASET}/first_round


# first round

# pot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode pot --stage first --data_path data/${DATASET}/first_round/pot.jsonl
# check_pot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_pot --stage first --data_path outputs/${DATASET}/pot/first/DEMO_pot_0_end.jsonl
# check_process_pot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_process_pot --stage first --data_path outputs/${DATASET}/check_pot/first/DEMO_check_pot_0_end.jsonl
# check_answer_pot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_answer_pot --stage first --data_path outputs/${DATASET}/check_process_pot/first/DEMO_check_process_pot_0_end.jsonl

# eot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode eot --stage first --data_path data/${DATASET}/first_round/eot.jsonl
# check_eot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_eot --stage first --data_path outputs/${DATASET}/eot/first/DEMO_eot_0_end.jsonl
# check_process_eot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_process_eot --stage first --data_path outputs/${DATASET}/check_eot/first/DEMO_check_eot_0_end.jsonl
# check_answer_eot first
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_answer_eot --stage first --data_path outputs/${DATASET}/check_process_eot/first/DEMO_check_process_eot_0_end.jsonl

python src/retrieve_data.py \
  --mode pot_error_first  \
  --plan_data outputs/${DATASET}/plan/DEMO_plan_0_end.jsonl \
  --pot_data outputs/${DATASET}/check_answer_pot/first/DEMO_check_answer_pot_0_end.jsonl \
  --output_dir data/${DATASET}/error_first


python src/retrieve_data.py \
  --mode eot_error_first  \
  --plan_data outputs/${DATASET}/plan/DEMO_plan_0_end.jsonl \
  --eot_data outputs/${DATASET}/check_answer_eot/first/DEMO_check_answer_eot_0_end.jsonl \
  --output_dir data/${DATASET}/error_first


# eot second data: pot_error
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode eot_error --stage second --data_path data/${DATASET}/error_first/pot_error_first.jsonl
# check_eot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_eot --stage second --data_path outputs/${DATASET}/eot_error/second/DEMO_eot_error_0_end.jsonl
# check_process_eot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_process_eot --stage second --data_path outputs/${DATASET}/check_eot/second/DEMO_check_eot_0_end.jsonl
# check_answer_eot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_answer_eot --stage second --data_path outputs/${DATASET}/check_process_eot/second/DEMO_check_process_eot_0_end.jsonl

# pot second data: eot_error
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode pot_error --stage second --data_path data/${DATASET}/error_first/eot_error_first.jsonl
# check_pot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_pot --stage second --data_path outputs/${DATASET}/pot_error/second/DEMO_pot_error_0_end.jsonl
# check_process_pot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_process_pot --stage second --data_path outputs/${DATASET}/check_pot/second/DEMO_check_pot_0_end.jsonl
# check_answer_pot second
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode check_answer_pot --stage second --data_path outputs/${DATASET}/check_process_pot/second/DEMO_check_process_pot_0_end.jsonl

python src/retrieve_data.py \
  --mode eot_pot_error_second  \
  --plan_data outputs/${DATASET}/plan/DEMO_plan_0_end.jsonl \
  --eot_data outputs/${DATASET}/check_answer_eot/first/DEMO_check_answer_eot_0_end.jsonl \
  --pot_data outputs/${DATASET}/check_answer_pot/first/DEMO_check_answer_pot_0_end.jsonl \
  --eot_data_2 outputs/${DATASET}/check_answer_eot/second/DEMO_check_answer_eot_0_end.jsonl \
  --pot_data_2 outputs/${DATASET}/check_answer_pot/second/DEMO_check_answer_pot_0_end.jsonl \
  --output_dir data/${DATASET}/error_second

# cot_error
python src/solve.py --tag DEMO --range_start 0 --range_end end --dataset ${DATASET} --model ${MODEL} --mode cot_error --data_path data/${DATASET}/error_second/eot_pot_error_second.jsonl

echo
echo "WoT reasoning has ended, please evaluate!"