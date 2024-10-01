import os
import json
import time
import copy
import wandb
import openai
import backoff
from time import sleep

import jsonlines

import argparse
from collections import Counter
from dataclasses import asdict
from tqdm import tqdm
from utils import get_var_assign
from brain import Brain

os.environ['WANDB_START_METHOD'] = 'thread'
os.environ['WANDB_MODE'] = 'offline'

def load_dataset(data_path):
    instances = []
    with open(data_path, "r+", encoding="utf8") as f:
        for inst in jsonlines.Reader(f):
            instances.append(inst)

    print(f"Load {len(instances)} data from {data_path}.")
    return instances


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default='', type=str)
    parser.add_argument("-d", "--dataset", default='gsm', type=str)
    parser.add_argument("-o", "--output_dir", default='outputs/', type=str)
    parser.add_argument("--stage", default='', type=str, help='first,second')
    parser.add_argument("--mode", required=True, type=str, help='cot, cot_error, pot, pot_error, eot, eot_error, peano, check_pot, check_process_pot, check_answer_pot, check_eot, check_process_eot, check_answer_eot')
    parser.add_argument("--range_start", default='0', type=str)
    parser.add_argument("--range_end", default='end', type=str)
    parser.add_argument("--tag", default='debug', type=str)
    parser.add_argument("--model", default='gpt-3.5-turbo-0613', type=str)
    parser.add_argument("--temperature", default=0, type=float)
    parser.add_argument("--key_group", default='a', type=str, help='api group')
    parser.add_argument("--org_id", default="", type=str, help='api organisation')
    parser.add_argument("--overwrite", default=True, type=bool)
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--enable_wandb", action='store_true')
    parser.add_argument("--wandb_entity", default='', type=str, help='wandb entity to login')
    # Brain args
    parser.add_argument("--max_turns", default=10, type=int)

    args = parser.parse_args()

    dataset_paths = {
        'gsm': 'data/gsm8k.jsonl',
        'gsmhard': 'data/gsmhard.jsonl',
        'algebra': 'data/algebra.jsonl',
        'addsub': 'data/mawpsaddsub.jsonl',
        'singleop': 'data/mawpssingleop.jsonl',
        'singleeq': 'data/mawpssingleeq.jsonl',
        'multiarith': 'data/mawpsmultiarith.jsonl',
        'svamp': 'data/svamp.jsonl',
    }

    if len(args.data_path) == 0:
        args.data_path = dataset_paths[args.dataset]

    args.output_dir = os.path.join(args.output_dir, args.dataset, args.mode, args.stage)

    if args.temperature > 0:
        args.tag = args.tag + f'_t{args.temperature}'
    args.tag = args.tag + f'_{args.mode}' + '_debug' if args.debug else args.tag + f'_{args.mode}'
    timestr = time.strftime("%m%d-%H%M%S")
    os.makedirs(args.output_dir, exist_ok=True)

    if not args.debug and args.enable_wandb:
        wandb.init(project='chatgpt',
                   entity=args.wandb_entity,
                   name=f"{args.dataset}_{args.tag}_{args.mode}",
                   config=vars(args),
                   save_code=True)
        # save code
        print(os.getcwd())
        wandb.run.log_code("./src")

    brain = Brain(args)

    # metrics
    correct = 0

    t_start = time.time()

    # ===== Loop =====
    data = []
    # with open(args.data_path, 'r') as file:
    #     for line in file:
    #         data.append(json.loads(line))

    try:
        with open(args.data_path, 'r', encoding='utf8') as file:
            for line in file:
                data.append(json.loads(line))
    except FileNotFoundError:
        print(f"File {args.data_path} not found. Returning an empty list.")
        data = []
        
    args.range_end = 10 if args.debug else args.range_end
    range_start = int(args.range_start)
    range_end = int(args.range_end) if args.range_end != 'end' else len(brain.data)
    inst_range = range(range_start, range_end)
    pbar = tqdm(inst_range)

    phase, method = '', ''  # phase: check/reason/reflection method: cot/pot/eot/peano/plan/pal/refine
    # origin check
    # if 'check_pot' in args.mode or 'check_eot' in args.mode:
    if 'check' in args.mode:
        phase = 'check'
    elif 'reflection' in args.mode:
        phase = 'reflection'
        method = args.mode.split('_')[-1]
    elif 'advice' in args.mode:
        phase = 'advice'
        method = args.mode.split('_')[-1]
    else:
        phase = 'reason'
        method = args.mode

    for inst_i in pbar:
        if phase == 'check':
            brain.set_instance_check(inst_i,data[inst_i]['id'])
            if args.mode == 'check_pot' or args.mode == 'check_eot':
                method = args.mode.split('_')[-1]
                brain.think_check(method)
            elif args.mode == 'check_process_pot':  # The program for adding the check pot process.
                brain.check_process_pot()
            elif args.mode == 'check_answer_pot':  # The program for adding the check pot answer.
                brain.check_answer_pot()
            elif args.mode == 'check_process_eot': # The program for adding the check eot process.
                brain.check_process_eot()
            elif args.mode == 'check_answer_eot': # The program for adding the check eot answer.
                brain.check_answer_eot()
        else:
            brain.set_instance(inst_i,data[inst_i]['id'], args)
            if method == 'plan':
                brain.plan()
            elif method == 'cot':
                brain.reason_cot()
            elif method == 'cot_error':
                brain.reason_cot_error()
            elif method == 'pot':
                brain.reason_pot()
            elif method == 'pot_error':
                brain.reason_pot_error()
            elif method == 'eot':
                brain.reason_eot()
            elif method == 'eot_error':
                brain.reason_eot_error()
            elif method == 'peano':
                brain.reason_peano()




        brain.save_cache()

        if inst_i % 20 == 0:
            brain.print_cache()

    t_end = time.time()

    metric = brain.get_metrics()
    print(f"========= Metric: {metric}")
    with open(os.path.join(args.output_dir, f'{args.tag}_metric.json'), 'w') as f:
        output_json = json.dumps(metric)
        f.write(output_json + '\n')

    if not args.debug and args.enable_wandb:
        wandb.log(metric)

    print(f"Save results at {brain.result_path}")
    print(f"Save metrics at {os.path.join(args.output_dir, f'{args.tag}_metric.json')}")
    print(f"Total inference time: {round((t_end - t_start) / 60, 4)} mins, "
          f"i.e. {round((t_end - t_start) / 3600, 4)} hours.")
