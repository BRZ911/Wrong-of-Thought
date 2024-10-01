import re
import os
import openai
import json
import time
import backoff
from time import sleep

import jsonlines

from prompts.plan import PLAN_SYSTEM, PLAN
from prompts.cot_complex import COT_SYSTEM, COT
from prompts.pot import POT_SYSTEM, POT
from prompts.eot import EOT_SYSTEM, EOT
from prompts.peano import PEANO_SYSTEM, PEANO
from prompts.check import ASSERT_SYSTEM, ASSERT_PROMPT
from prompts.self_refine import REFINE_SYSTEM, REFINE

from prompts.cot_complex_error import COT_ERROR_SYSTEM, COT_ERROR
from prompts.eot_error import EOT_ERROR_SYSTEM, EOT_ERROR
from prompts.pot_error import POT_ERROR_SYSTEM, POT_ERROR


from prompts.Check_Process_PoT import POT_PROCESS_SYSTEM, POT_PROCESS
from prompts.Check_Answer_PoT import POT_ANSWER_SYSTEM, POT_ANSWER
from prompts.Check_Process_EOT import EOT_PROCESS_SYSTEM, EOT_PROCESS
from prompts.Check_Answer_EOT import EOT_ANSWER_SYSTEM, EOT_ANSWER


from utils import *

openai.api_base = ""
KEY_GROUP = {
    'a': [
        ""
    ]
}


def load_dataset(data_path):
    instances = []
    try:
        with open(data_path, "r+", encoding="utf8") as f:
            for inst in jsonlines.Reader(f):
                instances.append(inst)
        print(f"Load {len(instances)} data from {data_path}.")
    except FileNotFoundError:
        print(f"File {data_path} not found. Returning an empty list.")
        return []
    return instances


class Brain:
    def __init__(self, args):

        self.args = args
        self.data = load_dataset(args.data_path)
        self.result_path = os.path.join(args.output_dir, f"{args.tag}_{args.range_start}_{args.range_end}.jsonl")

        if os.path.exists(self.result_path) and not args.overwrite:
            raise ValueError(f"Result file {self.result_path} already exists. Please set --overwrite to True.")
        elif os.path.exists(self.result_path) and args.overwrite:
            print(f"Result file {self.result_path} already exists. Will overwrite.")
            os.remove(self.result_path)

        print(f"Will save result at {self.result_path}")
        print(f"Will save metric at {os.path.join(args.output_dir, f'{args.tag}_metric.json')}")

        self.debug = args.debug
        if self.debug:
            print(f"===== Debug mode is on. =====")

        self.metrics = {
            'cot/correct': 0.0,
            'pot/correct': 0.0,
            'eot/correct': 0.0,
            'peano/correct': 0.0,
            'refine/correct': 0.0
        }

        self.KEYS = KEY_GROUP[args.key_group]
        print(f"Using KEY GROUP <{args.key_group}>, len: {len(self.KEYS)}")
        self.ORG_ID = args.org_id if len(args.org_id) > 0 else None

    def set_instance(self, inst_i, instance_id, args):
        self.id = instance_id
        self.instance = self.data[inst_i]
        if args.mode in ['plan'] :
            self.cache = {
                'id': instance_id,
                'inst/question': self.instance['input'],
                'inst/gold_answer': float(self.instance['target'])
            }
        elif args.mode in ['cot', 'pot', 'eot'] :
            self.cache = {
                'id': instance_id,
                'inst/question': self.instance['inst/question'],
                'inst/gold_answer': float(self.instance['inst/gold_answer'])
            }
        elif args.mode == 'eot_error':
            self.cache = {
                'id': instance_id,
                'inst/question': self.instance['inst/question'],
                'inst/gold_answer': float(self.instance['inst/gold_answer']),
                'reason/pot': self.instance['reason/pot'],
                'reason/pot/ans': self.instance['reason/pot/ans']
            }
        elif args.mode == 'pot_error':
            self.cache = {
                'id': instance_id,
                'inst/question': self.instance['inst/question'],
                'inst/gold_answer': float(self.instance['inst/gold_answer']),
                'reason/eot': self.instance['reason/eot'],
                'reason/eot/equations': self.instance['reason/eot/equations'],
                'reason/eot/ans': self.instance['reason/eot/ans']}
        elif args.mode == 'cot_error':
            self.cache = {
                'id': instance_id,
                'inst/question': self.instance['inst/question'],
                'inst/gold_answer': float(self.instance['inst/gold_answer']),
                'reason/pot': self.instance['reason/pot'],
                'reason/pot/ans': self.instance['reason/pot/ans'],
                'reason/eot': self.instance['reason/eot'],
                'reason/eot/equations': self.instance['reason/eot/equations'],
                'reason/eot/ans': self.instance['reason/eot/ans']
                }
        

        self.api_key = self.KEYS[instance_id % len(self.KEYS)]

    def set_instance_check(self, inst_i, instance_id):
        self.id = instance_id
        self.instance = self.data[inst_i]
        self.cache = {k: v for k, v in self.instance.items()}
        self.api_key = self.KEYS[instance_id % len(self.KEYS)]


    def plan(self):
        """
        Plan the reasoning method.
        """
        question = self.cache["inst/question"]
        chat_input = self.build_chat_input(PLAN_SYSTEM, PLAN.format(question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['plan'] = response

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input}")
            print(f"response: {response}")

    def reason_cot(self):
        """
        Reasoning with Chain-of-Thought, prompts from COT
        """
        question = self.cache["inst/question"]
        chat_input = self.build_chat_input(COT_SYSTEM, COT.format(question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/cot'] = response

        # execute
        answer_format_flag = 'The answer is' in response
        pred_str = response.split('The answer is')[-1].strip('.').replace(',', '').strip()

        try:
            all_digit = re.findall(r"[-+]?\d*\.?\d+|\d+", pred_str)
            if answer_format_flag:
                pred = all_digit[0]
            else:
                pred = all_digit[-1]
            pred = floatify_ans(pred)
            if pred is not None and '%' in pred_str:
                pred = pred / 100
        except Exception as e:
            print(e)
            print(pred_str)
            pred = None
        score = 0.0
        if pred is not None:
            score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        self.cache['reason/cot/ans'] = pred
        self.cache['reason/cot/score'] = score
        self.metrics['cot/correct'] += score

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input}")
            print(f"response: {response}")
            print(f"score: {score}")

    def reason_cot_error(self):
        """
        Reasoning with Chain-of-Thought, prompts from COT
        """
        question = self.cache["inst/question"]
        reason_pot = self.instance['reason/pot']
        reason_pot_ans = self.instance['reason/pot/ans']
        reason_eot = self.instance['reason/eot']
        reason_eot_equations = self.instance['reason/eot/equations']
        reason_eot_ans = self.instance['reason/eot/ans']
        chat_input = self.build_chat_input(COT_ERROR_SYSTEM, COT_ERROR.format(question=question, reason_pot=reason_pot, reason_pot_ans=reason_pot_ans, reason_eot=reason_eot, reason_eot_equations=reason_eot_equations, reason_eot_ans=reason_eot_ans))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/cot'] = response

        # execute
        answer_format_flag = 'The answer is' in response
        pred_str = response.split('The answer is')[-1].strip('.').replace(',', '').strip()

        try:
            all_digit = re.findall(r"[-+]?\d*\.?\d+|\d+", pred_str)
            if answer_format_flag:
                pred = all_digit[0]
            else:
                pred = all_digit[-1]
            pred = floatify_ans(pred)
            if pred is not None and '%' in pred_str:
                pred = pred / 100
        except Exception as e:
            print(e)
            print(pred_str)
            pred = None
        score = 0.0
        if pred is not None:
            score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        self.cache['reason/cot/ans'] = pred
        self.cache['reason/cot/score'] = score
        self.metrics['cot/correct'] += score

    def reason_pot(self):
        """
        Reason with Program-of-Thought, prompts from PAL
        """
        question = self.cache["inst/question"]
        chat_input = self.build_chat_input(POT_SYSTEM, POT.format(question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/pot'] = response

        if '```python' in response:
            start_index = response.find("python")

            start_index += len("python")
            end_index = response.find("```", start_index)

            if end_index == -1:
                response = response[start_index:].strip()
            else:
                response = response[start_index:end_index].strip()

        # execute
        score = 0.0
        try:
            pred = safe_execute(response)
            pred = floatify_ans(pred)
            if pred is not None:
                score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        except Exception as e:
            pred = None
            score = 0.0
        self.cache['reason/pot/ans'] = pred
        self.cache['reason/pot/score'] = score
        self.metrics['pot/correct'] += score

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input}")
            print(f"response: {response}")
            print(f"score: {score}")

    def reason_pot_error(self):
        """
        Reason with Program-of-Thought, prompts from PAL
        """
        question = self.cache["inst/question"]
        reason_eot = self.instance['reason/eot']
        reason_eot_equations = self.instance['reason/eot/equations']
        chat_input = self.build_chat_input(POT_ERROR_SYSTEM, POT_ERROR.format(reason_eot=reason_eot,reason_eot_equations=reason_eot_equations,question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        # print(response)
        self.cache['reason/pot'] = response
        
        if '```python' in response:
            start_index = response.find("python")

            start_index += len("python")
            end_index = response.find("```", start_index)

            if end_index == -1:
                response = response[start_index:].strip()
            else:
                response = response[start_index:end_index].strip()

        # execute
        score = 0.0
        try:
            pred = safe_execute(response)
            pred = floatify_ans(pred)
            if pred is not None:
                score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        except Exception as e:
            pred = None
            score = 0.0
        self.cache['reason/pot/ans'] = pred
        self.cache['reason/pot/score'] = score
        self.metrics['pot/correct'] += score


    def check_process_pot(self):
        # print('check_process_pot')
        question = self.cache["inst/question"]
        reason_pot = self.instance['reason/pot']
        reason_pot_ans = self.instance['reason/pot/ans']
        if reason_pot_ans is None:
            self.cache['check/process/pot'] = 'The answer is NULL, which is directly judged as an error.'
            self.cache['check/process/pot/flag'] = 0
            # print('reason_pot_ans is None')
        else:
            chat_input = self.build_chat_input(POT_PROCESS_SYSTEM, POT_PROCESS.format(reason_pot=reason_pot,question=question))
            response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
            self.cache['check/process/pot'] = response
            # print(response)
            check_flag = response.split("Decision:")[-1].replace(",", "").lower()
            if 'right' in check_flag or 'correct' in check_flag or 'yes' in check_flag:
                self.cache['check/process/pot/flag'] = 1
            else :
                self.cache['check/process/pot/flag'] = 0

    def check_answer_pot(self):
        """
        Reason with Program-of-Thought, prompts from PAL
        """
        question = self.cache["inst/question"]
        reason_pot = self.instance['reason/pot']
        reason_pot_ans = self.instance['reason/pot/ans']
        if reason_pot_ans is None:
            self.cache['check/answer/pot/flag'] = 0
            self.cache['check/answer/pot'] = 'The answer is NULL, which is directly judged as an error.'
            # print('reason_pot_ans is None')
        else:
            chat_input = self.build_chat_input(POT_ANSWER_SYSTEM, POT_ANSWER.format(reason_pot=reason_pot,reason_pot_ans=reason_pot_ans,question=question))
            response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
            self.cache['check/answer/pot'] = response
            # print(response)
            check_flag = response.split("Decision:")[-1].replace(",", "").lower()
            if 'right' in check_flag or 'correct' in check_flag or 'yes' in check_flag:
                self.cache['check/answer/pot/flag'] = 1
            else :
                self.cache['check/answer/pot/flag'] = 0

        count_ones = self.instance['think/check/pot/flag'] + self.instance['check/process/pot/flag']+ self.cache['check/answer/pot/flag']
        
        if count_ones > 1 :
            self.cache['check/final/pot/flag'] = 1
        else:
            self.cache['check/final/pot/flag'] = 0

    def reason_eot(self):
        """
        Reason with Equation-of-Thought
        """
        question = self.cache["inst/question"]
        chat_input = self.build_chat_input(EOT_SYSTEM, EOT.format(question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/eot'] = response

        # execute
        pattern = r'\s*\(\d+\)$'
        equations = []
        for line in response.split('\n'):
            if '=' in line:
                line = '='.join(line.split('=')[:2])
                equations.append(line.strip())
            else:
                continue

        try:
            solutions = safe_solve_equation_system(equations)
            pred = floatify_ans(solutions['ans'])
            score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        except Exception as e:
            if self.debug:
                print(e)
            pred = None
            score = 0.0

        self.cache['reason/eot/equations'] = equations
        self.cache['reason/eot/ans'] = pred
        self.cache['reason/eot/score'] = score
        self.metrics['eot/correct'] += score

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input}")
            print(f"response: {response}")
            print(f"equations: {equations}")
            print(f"score: {score}")


    def check_process_eot(self):
        """
        Reason with Program-of-Thought, prompts from PAL
        """
        question = self.cache["inst/question"]
        # reason_eot = self.instance['reason/eot'] + ". Error result:" + str(self.instance['reason/eot/ans'])
        reason_eot = self.instance['reason/eot']
        # reason_eot_equations = self.instance['reason/eot/equations']
        reason_eot_ans = self.instance['reason/eot/ans']
        if reason_eot_ans is None:
            self.cache['check/process/eot/flag'] = 0
            self.cache['check/process/eot'] = 'The answer is NULL, which is directly judged as an error.'
            # print('reason_eot_ans is None')
        else:
            chat_input = self.build_chat_input(EOT_PROCESS_SYSTEM, EOT_PROCESS.format(reason_eot=reason_eot,question=question))
            response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
            self.cache['check/process/eot'] = response
            # print(response)
            check_flag = response.split("Decision:")[-1].replace(",", "").lower()
            if 'right' in check_flag or 'correct' in check_flag or 'yes' in check_flag:
                self.cache['check/process/eot/flag'] = 1
            else :
                self.cache['check/process/eot/flag'] = 0

    def check_answer_eot(self):
        question = self.cache["inst/question"]
        reason_eot_equations = self.instance['reason/eot/equations']
        reason_eot_ans = self.instance['reason/eot/ans']
        if reason_eot_ans is None:
            self.cache['check/answer/eot'] = 'The answer is NULL, which is directly judged as an error.'
            self.cache['check/answer/eot/flag'] = 0
            # print('reason_eot_ans is None')
        else:
            chat_input = self.build_chat_input(EOT_ANSWER_SYSTEM, EOT_ANSWER.format(reason_eot_equations=reason_eot_equations, reason_eot_ans=reason_eot_ans, question=question))
            response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
            self.cache['check/answer/eot'] = response
            # print(response)
            check_flag = response.split("Decision:")[-1].replace(",", "").lower()
            if 'right' in check_flag or 'correct' in check_flag or 'yes' in check_flag:
                self.cache['check/answer/eot/flag'] = 1
            else :
                self.cache['check/answer/eot/flag'] = 0

        # print(self.cache['check/answer/eot/flag'])
        count_ones = self.instance['think/check/eot/flag'] + self.instance['check/process/eot/flag']+ self.cache['check/answer/eot/flag']
        
        if count_ones > 1 :
            self.cache['check/final/eot/flag'] = 1
        else:
            self.cache['check/final/eot/flag'] = 0

    def reason_eot_error(self):
        """
        Reason with Equation-of-Thought
        """
        question = self.cache["inst/question"]
        reason_pot = self.cache["reason/pot"]
        chat_input = self.build_chat_input(EOT_ERROR_SYSTEM, EOT_ERROR.format(question=question, reason_pot=reason_pot))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/eot'] = response
        # print('response',response)

        response = response.split('Equations:')[-1]

        # execute
        pattern = r'\s*\(\d+\)$'
        equations = []
        for line in response.split('\n'):
            if '=' in line:
                line = '='.join(line.split('=')[:2])
                equations.append(line.strip())
            else:
                continue

        try:
            solutions = safe_solve_equation_system(equations)
            pred = floatify_ans(solutions['ans'])
            score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        except Exception as e:
            if self.debug:
                print(e)
            pred = None
            score = 0.0

        self.cache['reason/eot/equations'] = equations
        self.cache['reason/eot/ans'] = pred
        self.cache['reason/eot/score'] = score
        self.metrics['eot/correct'] += score



    def reason_peano(self):
        """
        Reason with Peano, from https://arxiv.org/pdf/2304.09102.pdf
        :return:
        """
        question = self.cache["inst/question"]
        chat_input = self.build_chat_input(PEANO_SYSTEM, PEANO.format(question=question))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache['reason/peano'] = response

        # execute
        eq_list = re.findall(r'\[\[.*?\]\]', response)

        def reformat_incre_equations(x):
            result = ''
            if len(x) >= 1:
                for eq in x:
                    if len(result) == 0:
                        result += eq[2: -2]
                    else:
                        result += ', ' + eq[2: -2]
            return result

        def reformat_equations_from_peano(eq_list):
            result = ''
            for eq in eq_list.split(','):
                if 'eq' in eq:
                    if len(result) == 0:
                        result += eq[eq.index('eq') + 2:]
                    else:
                        result += ', ' + eq[eq.index('eq') + 2:]
                elif 'answer' in eq:
                    if len(result) == 0:
                        result += eq[eq.index('answer') + 6:].strip() + ' = ?'
                    else:
                        result += ', ' + eq[eq.index('answer') + 6:].strip() + ' = ?'
            return result

        if len(eq_list) > 0:
            eq_list = reformat_equations_from_peano(reformat_incre_equations(eq_list))

        answer = get_final_using_sympy(eq_list)
        try:
            score = 1.0 if abs(float(answer) - float(self.cache['inst/gold_answer'])) < 1e-3 else 0.0
        except Exception as e:
            print(e)
            score = 0.0

        self.cache['reason/peano/ans'] = answer
        self.cache['reason/peano/score'] = score
        self.metrics['peano/correct'] += score

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input}")
            print(f"response: {response}")
            print(f"ans: {answer}")
            print(f"gold: {self.cache['inst/gold_answer']}")
            print(f"score: {score}")


    def think_check(self, method='pot'):
        """
        Think moduel: Check
        For PoT, check with ASSERT
        """
        question = self.cache["inst/question"]
        pred = self.cache[f'reason/{method}/ans']

        if method == 'pot':
            code = self.cache[f'reason/{method}']
            variables = get_stepwise_exec_results(code, method)
        elif method == 'eot':
            code = self.cache[f'reason/{method}/equations']
            try:
                var_dict = safe_solve_equation_system(code)
                all_var_name = sort_words_by_first_appearance(list(var_dict.keys()), ' '.join(code))
                all_var_name = [name for name in all_var_name if name != 'x' and name != 'ans']
                variables = [f"{name} = {var_dict[name]}" for name in all_var_name]

            except Exception as e:
                variables = code
        else:
            raise NotImplementedError(f"Method {method} not supported")

        chat_input = self.build_chat_input(ASSERT_SYSTEM, ASSERT_PROMPT.format(question=question,
                                                                               variables='\n'.join(variables)))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache[f'think/check/{method}/variables'] = variables
        self.cache[f'think/check/{method}'] = response

        if '```python' in response:
            start_index = response.find("python")

            start_index += len("python")
            end_index = response.find("```", start_index)

            if end_index == -1:
                response = response[start_index:].strip()
            else:
                response = response[start_index:end_index].strip()

        # execute
        if method == 'pot':
            code = variables + [f"ans = {pred}"] + [response]
        elif method == 'eot':
            code = [f"x = {pred}"] + variables + [f"ans = x"] + [response]
        code_str = '\n'.join(code)

        check_flag = False if timeout_exec(code_str) is None else True



        self.cache[f'think/check/{method}/flag'] = int(check_flag)

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"code: {code_str}")
            print(f"response: {response}")
            print(f"score: {self.cache[f'reason/{method}/score']}")
            print(f"flag: {check_flag}")


    def think_refine(self):
        """
        Self-refine on PAL
        """
        code = self.cache['reason/pot']
        chat_input = self.build_chat_input(REFINE_SYSTEM, REFINE.format(code=code))
        response = get_chat_response(self.args, chat_input, self.api_key, self.ORG_ID)
        self.cache[f'think/refine'] = response

        # execute
        score = 0.0
        try:
            code = extract_code(response)
            code = [line for line in code.split('\n') if 'print' not in line]
            pred = safe_execute_func("\n".join(code))
            pred = floatify_ans(pred)
            if pred is not None:
                score = 1.0 if abs(pred - self.cache['inst/gold_answer']) < 1e-3 else 0.0
        except Exception as e:
            pred = None
            score = 0.0
        self.cache['think/refine/ans'] = pred
        self.cache['think/refine/score'] = score
        self.metrics['refine/correct'] += score

        if self.debug:
            print(f"=== inst i: {self.id} ===")
            print(f"chat_input: {chat_input_to_string(chat_input)}")
            print(f"response: {response}")
            print(f"ori_score: {self.cache['reason/pot/score']}")
            print(f"refine_score: {score}")


    def save_cache(self):
        with open(self.result_path, 'a') as out_f:
            output_json = json.dumps(self.cache)
            out_f.write(output_json + '\n')

    def print_cache(self):
        for k, v in self.cache.items():
            print(f"{k}: {v}")

    def get_metrics(self):
        self.metrics['cot/acc'] = self.metrics['cot/correct'] / len(self.data)
        self.metrics['pot/acc'] = self.metrics['pot/correct'] / len(self.data)
        self.metrics['eot/acc'] = self.metrics['eot/correct'] / len(self.data)
        self.metrics['peano/acc'] = self.metrics['peano/correct'] / len(self.data)
        self.metrics['refine/acc'] = self.metrics['refine/correct'] / len(self.data)

        self.metrics['total'] = len(self.data)
        return self.metrics


    @staticmethod
    def build_chat_input(instruction, user_input):
        return [
            {"role": "system", "content": instruction},
            {"role": "user", "content": user_input},
        ]
