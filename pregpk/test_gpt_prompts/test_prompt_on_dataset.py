import sys
import os
import json
import time
import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from openai import OpenAI
from pkdb.utilities import gpt_utils, testing_utils, file_utils, analysis_utils


# TODO: Way to store how many tokens are being used per query/experiment
# TODO: Maybe add way to add a seed to randomization of selecting test set

def main(dataset_path, prompt_path, results_directory, test_set_params, gpt_params):
    with open(dataset_path, 'r') as jf:
        dataset = json.loads(jf.read())
    dataset = pd.DataFrame.from_dict(dataset, orient='index')

    test_set = testing_utils.test_set_from_full_dataset(dataset, test_set_params, random_seed=None)
    test_set = testing_utils.make_article_queries(test_set)
    test_set["query_tokens"] = test_set.apply(
        lambda row: gpt_utils.num_tokens_from_string(string=row["query"], gpt_model=gpt_params["version"]),
        axis=1)

    base_query = [{"role": "system", }]
    with open(prompt_path, 'r') as f:
        base_query[0]["content"] = f.read()
    base_prompt_tokens = gpt_utils.num_tokens_from_string(base_query[0]['content'])

    with open(os.path.join('user_data','initials.txt'), 'r') as f:
        user_initials = f.read()
    with open(os.path.join('user_data','chatgpt_api_key.txt'), 'r') as f:
        chatgpt_api_key = f.read()
    client = OpenAI(api_key=chatgpt_api_key)

    results = {
        "user": user_initials,
        "dataset": os.path.basename(dataset_path),
        "gpt_params": gpt_params,
        "prompt": base_query,
        "prompt_file": os.path.basename(prompt_path),
        "balanced": test_set_params["balance_classes"],
        "n_articles": test_set_params["n"],
        "estimated_cost": 0.0,
        "results": []
    }

    total_cost = gpt_utils.cost_per_token(gpt_params['version'], output=False) * base_prompt_tokens * test_set_params['n'] + \
                 gpt_utils.cost_per_token(gpt_params['version'], output=False) * test_set['query_tokens'].sum() + \
                 gpt_utils.cost_per_token(gpt_params['version'], output=True) * gpt_params['max_tokens'] * test_set_params['n']
    results["estimated_cost"] = total_cost

    proceed = bool(int(input(f"This test will cost about ${total_cost:.4f}.\nProceed? [0:no or 1:yes]\n") or "1"))
    if not proceed:
        sys.exit("User chose not to run test.\n")

    try:
        last_experiment = file_utils.get_last_experiment_number(results_directory)
    except IndexError:
        last_experiment = -1  # In case
    results_path = os.path.join(results_directory, f"{last_experiment + 1}.json")
    for i, (pmid, row) in enumerate(tqdm(test_set.iterrows(), total=len(test_set))):

        completion = client.chat.completions.create(
            model=gpt_params["version"],
            temperature=gpt_params["temperature"],
            max_tokens=gpt_params["max_tokens"],
            messages=base_query + [{"role": "user", "content": row['query']}]
        )

        ret = completion.choices[0].message.content[0]  # First character
        if ret == '1':
            pred = True
        elif ret == '0':
            pred = False
        else:
            pred = -1

        results["results"].append(
            {'pmid': pmid,
             'has_pk_data': row['has_pk_data'],
             'gpt_pred': pred,
             'gpt_response': ret,
             }
        )

        if i % 10 == 0:
            with open(results_path, 'w') as results_out_file:
                json_object = json.dumps(results, indent=4)
                results_out_file.write(json_object)

    with open(results_path, 'w') as results_out_file:
        json_object = json.dumps(results, indent=4)
        results_out_file.write(json_object)

    print(f'\nResults saved in {results_path}\n')
    print(analysis_utils.study_summary(results))

    return


def get_input_advanced_testing_params():
    print("Advanced settings (Just press ENTER for default option in any setting):")

    print("Set testing dataset parameters:")
    bc = input("\tBalance the classes [0:no, 1:yes (default)]?\t") or "1"
    try:
        bc = bool(int(bc))
    except:
        print('\tInput invalid. Defaulting to YES.')
        bc = True

    n = input("\tTotal number of articles in dataset [default = 40]:\t") or "40"
    try:
        n = int(n)
    except:
        print('\tInput invalid. Defaulting to 40.')
        n = 40

    print("Set GPT parameters:")
    vers = input('\tGPT Version ["gpt-4", "gpt-4-0125-preview", or "gpt-3.5-turbo-0125" (default)]:\t') or "gpt-3.5-turbo-0125"
    if vers not in ["gpt-4", "gpt-4-0125-preview", "gpt-3.5-turbo-0125"]:
        print('\tInput invalid. Defaulting to "gpt-3.5-turbo-0125".')
        vers = "gpt-3.5-turbo-0125"

    temp = input('\tTemperature [value from 0 to 2, default 0.1]:\t') or "0.1"
    try:
        temp = float(temp)
        if temp < 0 or temp > 2:
            print('\tInput invalid. Defaulting to 0.1.')
            temp = 0.1
    except:
        print('\tInput invalid. Defaulting to 0.1.')
        temp = 0.1

    max_tokens = input("\tMax tokens [default = 50]:\t") or "50"
    try:
        max_tokens = int(max_tokens)
    except:
        print('\tInput invalid. Defaulting to 50.')
        max_tokens = 50
    print('')

    test_set_params = {"balance_classes": bc,
                       "n": n,}
    gpt_params = {"version": vers,
                  "temperature": temp,
                  "max_tokens": max_tokens}

    return test_set_params, gpt_params


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print('')

    dataset_dir = "datasets"
    prompt_dir = "prompts"
    results_dir = "results"

    dataset_filename = "20240327_ta.json"
    prompt_filename = "1.txt"

    use_gui = True
    tk.Tk().withdraw()
    if use_gui:
        dataset_filename = file_utils.get_most_recent_text_dated_filename(dataset_dir)
        prompt_filename = tk.filedialog.askopenfilename(
            initialdir=os.path.join(os.getcwd(), prompt_dir), title='Prompt file', filetypes=(('Text files', '*.txt'),))
    dataset_file = os.path.join(dataset_dir, dataset_filename)
    prompt_file = os.path.join(prompt_dir, prompt_filename)

    test_set_parameters = {"balance_classes": True,
                           "n": 40, }

    # ['gpt-4', 'gpt-4-0125-preview', 'gpt-4-1106-preview', 'gpt-3.5-turbo-0125']
    gpt_parameters = {"version": "gpt-3.5-turbo-0125",
                      "temperature": 0.1,
                      "max_tokens": 100, }

    if 'adv' in sys.argv:
        test_set_parameters, gpt_parameters = get_input_advanced_testing_params()

    main(dataset_file, prompt_file, results_dir, test_set_parameters, gpt_parameters)
    input()