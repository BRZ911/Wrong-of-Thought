import os
import json
import time
import logging
import random
import argparse
import pandas as pd

from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np
from tabulate import tabulate
from collections import Counter

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, type=str, help='plan, pot_error_first, eot_error_first, eot_pot_error_second')
    parser.add_argument("--plan_data", default='', type=str)
    parser.add_argument("--pot_data", default=None, type=str)
    parser.add_argument("--eot_data", default=None, type=str)
    parser.add_argument("--pot_data_2", default=None, type=str)
    parser.add_argument("--eot_data_2", default=None, type=str)
    parser.add_argument("--output_dir", default='', type=str)

    random.seed(42)

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)


    def load_result(path):
        instances = []
        try:
            with open(path, 'r', encoding='utf8') as f:
                for line in f.readlines():
                    instances.append(json.loads(line.strip()))
        except FileNotFoundError:
            print(f"File {path} not found. Returning an empty list.")
            return []
        
        return instances
    

    plan_data = load_result(args.plan_data)

    if args.pot_data is not None:
        pot_data = load_result(args.pot_data)

    if args.eot_data is not None:
        eot_data = load_result(args.eot_data)

    if args.pot_data_2 is not None:
        pot_data_2 = load_result(args.pot_data_2)

    if args.eot_data_2 is not None:
        eot_data_2 = load_result(args.eot_data_2)
    
    data_len = len(plan_data)

# Step 1, retrieve the data after the plan
    if args.mode == 'plan':
            if plan_data is not None:
                eot = []
                pot = []
                for i in range(data_len):
                    plan_method = plan_data[i]['plan']

                    if 'equations' in plan_method:
                        eot.append(plan_data[i])

                    elif 'Python' in plan_method:
                        pot.append(plan_data[i])
                    else:
                        pot.append(plan_data[i])

            else :
                print("Plan_data data not inputted")


            with open(f"{args.output_dir}/pot.jsonl", 'w') as file:
                for item in pot:
                    json.dump(item, file)
                    file.write('\n')

            with open(f"{args.output_dir}/eot.jsonl", 'w') as file:
                for item in eot:
                    json.dump(item, file)
                    file.write('\n')

            print(f"The planned EOT and POT have been saved to {args.output_dir}")

# Step 2, retrieve the data with pot errors.
    if args.mode == 'pot_error_first':
        pot_assertion_data = pd.DataFrame(pot_data)
        pot_error = []

        # ===== Plan =====
        if plan_data is not None:
            for i in range(data_len):
                plan_method = plan_data[i]['plan']

                if 'equations' not in plan_method:
                    if pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['check/final/pot/flag'] == 0:
                        pot_error.append(pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0])

            with open(f"{args.output_dir}/pot_error_first.jsonl", 'w') as file:
                for item in pot_error:
                    json.dump(item, file)
                    file.write('\n')
    
        print(f"The pot_error_first have been saved to {args.output_dir}")

# Step 3, retrieve the data with eot errors.
    if args.mode == 'eot_error_first':
        eot_assertion_data = pd.DataFrame(eot_data)
        print(eot_data)

        eot_error = []

        # ===== Plan =====
        if plan_data is not None:
            for i in range(data_len):
                plan_method = plan_data[i]['plan']

                if 'equations' in plan_method:
                    if eot_assertion_data[eot_assertion_data['id'] == i].to_dict('records')[0]['check/final/eot/flag'] == 0:
                        eot_error.append(eot_assertion_data[eot_assertion_data['id'] == i].to_dict('records')[0])

            with open(f"{args.output_dir}/eot_error_first.jsonl", 'w') as file:
                for item in eot_error:
                    json.dump(item, file)
                    file.write('\n')
        print(f"The eot_error_first have been saved to {args.output_dir}")

# Step 4, retrieve the data with second pot and eot errors.
    if args.mode == 'eot_pot_error_second':

        eot_assertion_data = pd.DataFrame(eot_data)
        pot_assertion_data = pd.DataFrame(pot_data)
        eot_assertion_data_2 = pd.DataFrame(eot_data_2)
        pot_assertion_data_2 = pd.DataFrame(pot_data_2)

        error = []

        # ===== Plan =====
        if plan_data is not None:
            for i in range(data_len):
                plan_method = plan_data[i]['plan']

                # What we want to obtain here is the error in the second stage.
        
                if 'equations' in plan_method:
                    if eot_assertion_data[eot_assertion_data['id'] == i].to_dict('records')[0]['check/final/eot/flag'] == 0:
                        if pot_assertion_data_2[pot_assertion_data_2['id'] == i].to_dict('records')[0]['check/final/pot/flag'] == 0:
                            error.append(pot_assertion_data_2[pot_assertion_data_2['id'] == i].to_dict('records')[0])

                else:
                    if pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['check/final/pot/flag'] == 0:
                        if eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0]['check/final/eot/flag'] == 0:
                            error.append(eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0])

            with open(f"{args.output_dir}/eot_pot_error_second.jsonl", 'w') as file:
                for item in error:
                    json.dump(item, file)
                    file.write('\n')

        print(f"The eot_pot_error_second have been saved to {args.output_dir}")

            
            