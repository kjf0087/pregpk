import os
import json
import numpy as np
import sklearn.metrics


def study_confusion_matrix(results:dict):

    y_true = [i['has_pk_data'] for i in results["results"] if i['gpt_pred'] != -1]  # Remove errors
    y_pred = [i['gpt_pred'] for i in results['results'] if i['gpt_pred'] != -1]

    return np.flip(sklearn.metrics.confusion_matrix(y_true, y_pred), axis=(0, 1))


def conf_mat_string(cm):
    s = list(str(cm))  # Start just with the CM
    s = list('  Pred\n') + s  # Add "predicted" label

    shift1 = len('Actual ')
    s2 = [" "]*shift1
    for c in s:  # If newline, change with newline plus shift to account for "Actual "
        s2.append(c)
        if c == '\n':
            s2 += list(f'{" "*shift1}')
    s = s2

    s[s.index('[')-shift1:s.index('[')] = list('Actual ')  # Add "Actual "
    return "".join(s)


def study_summary(results:dict) -> str:

    n_disp = results['n_articles']
    n_errors_disp = len([i for i in results['results'] if i['gpt_pred'] == -1])
    dataset_disp = results['dataset']
    prompt_disp = results['prompt_file']

    cm = study_confusion_matrix(results)
    disp_cm = conf_mat_string(cm)
    disp_cm = disp_cm.replace('\n', f'\n{" " * 20}')
    prec = cm[0, 0] / (cm[0, 0] + cm[1, 0])
    rec = cm[0, 0] / (cm[0, 0] + cm[0, 1])
    f1 = cm[0, 0] / (cm[0, 0] + 0.5 * (cm[1, 0] + cm[0, 1]))

    summary = f"{'Dataset:':<20}{dataset_disp}\n" \
              f"{'n/errors:':<20}{n_disp}/{n_errors_disp}\n" \
              f"{'GPT Version:':<20}{results['gpt_params']['version']}\n" \
              f"{'Prompt:':<20}{prompt_disp}\n" \
              f"{'Cost:':<20}${results['estimated_cost']:.3f}\n" \
              f"{'Metrics:':<20}prec: {prec:.3f}\n" \
              f"{' ' * 20}rec:  {rec:.3f}\n" \
              f"{' ' * 20}F1:   {f1:.3f}\n" \
              f"{'Conf. mat.:':<20}{disp_cm}"

    return summary


def all_study_summaries(results_directory:str="results"):

    studies = sorted([i for i in os.listdir(results_directory) if i.endswith('.json')])
    for study in studies:
        study_disp = study[:study.index('.')]
        print(f"Study {study_disp}:")

        with open(os.path.join(results_directory, study), 'r') as jf:
            results = json.loads(jf.read())
            i_summary = '\t' + study_summary(results)
            print(i_summary.replace('\n', '\n\t'), '\n')
