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
    parser.add_argument("--mode", required=True, type=str, help='analyze')
    parser.add_argument("--plan_data", default='', type=str)
    parser.add_argument("--pot_data", default=None, type=str)
    parser.add_argument("--eot_data", default=None, type=str)
    parser.add_argument("--pot_data_2", default=None, type=str)
    parser.add_argument("--eot_data_2", default=None, type=str)
    parser.add_argument("--cot_data", default=None, type=str)

    random.seed(42)

    args = parser.parse_args()


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

    if args.cot_data is not None:
        cot_data = load_result(args.cot_data)
    
    data_len = len(plan_data)

# Step 4, retrieve the data with second pot and eot errors.
    if args.mode == 'analyze':

        plan_assert_acc = 0
        unknown_plan_cnt = 0
        steps_sum = 0
        pec_cnt = {
            'p': 0, 'e': 0, 'c': 0
        }

        eot_assertion_data = pd.DataFrame(eot_data)
        pot_assertion_data = pd.DataFrame(pot_data)
        eot_assertion_data_2 = pd.DataFrame(eot_data_2)
        pot_assertion_data_2 = pd.DataFrame(pot_data_2)
        cot_assertion_data = pd.DataFrame(cot_data)

        error = []

        # ===== Plan =====
        if plan_data is not None:
            for i in range(data_len):
                plan_method = plan_data[i]['plan']

                # What we want to obtain here is the error in the second stage.
        
                if 'equations' in plan_method:
                    if eot_assertion_data[eot_assertion_data['id'] == i].to_dict('records')[0]['check/final/eot/flag']:
                        plan_assert_acc += eot_assertion_data[eot_assertion_data['id'] == i].to_dict('records')[0]['reason/eot/score']
                        steps_sum += 1
                        pec_cnt['e'] += 1
                    elif pot_assertion_data_2[pot_assertion_data_2['id'] == i].to_dict('records')[0]['check/final/pot/flag']:
                        plan_assert_acc += pot_assertion_data_2[pot_assertion_data_2['id'] == i].to_dict('records')[0]['reason/pot/score']
                        steps_sum += 2
                        pec_cnt['p'] += 1
                    else :
                        plan_assert_acc += cot_assertion_data[cot_assertion_data['id'] == i].to_dict('records')[0]['reason/cot/score']
                        steps_sum += 3
                        pec_cnt['c'] += 1

                elif 'Python' in plan_method:
                    if pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['check/final/pot/flag']:
                        plan_assert_acc += pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['reason/pot/score']
                        steps_sum += 1
                        pec_cnt['p'] += 1
                    elif eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0]['check/final/eot/flag']:
                        plan_assert_acc += eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0]['reason/eot/score']
                        steps_sum += 2
                        pec_cnt['e'] += 1
                    else :
                        plan_assert_acc += cot_assertion_data[cot_assertion_data['id'] == i].to_dict('records')[0]['reason/cot/score']
                        steps_sum += 3
                        pec_cnt['c'] += 1

                else:
                    if pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['check/final/pot/flag']:
                        plan_assert_acc += pot_assertion_data[pot_assertion_data['id'] == i].to_dict('records')[0]['reason/pot/score']
                        steps_sum += 1
                        pec_cnt['p'] += 1
                    elif eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0]['check/final/eot/flag']:
                        plan_assert_acc += eot_assertion_data_2[eot_assertion_data_2['id'] == i].to_dict('records')[0]['reason/eot/score']
                        steps_sum += 2
                        pec_cnt['e'] += 1
                    else :
                        plan_assert_acc += cot_assertion_data[cot_assertion_data['id'] == i].to_dict('records')[0]['reason/cot/score']
                        steps_sum += 3
                        pec_cnt['c'] += 1

                    unknown_plan_cnt += 1

            print(f"===== WoT main results =====")
            print(plan_assert_acc / data_len)
            print(f"Avg Steps: {steps_sum / data_len}")
            print(f"Unknown plan method: {unknown_plan_cnt}")
            print(f"===== PEC ratio =====")
            print(f"PoT: {pec_cnt['p']},{pec_cnt['p'] / data_len}, EoT: {pec_cnt['e']}, {pec_cnt['e'] / data_len},"
                        f"CoT: {pec_cnt['c']},{pec_cnt['c'] / data_len}")