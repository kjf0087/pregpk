import os


def get_most_recent_text_dated_filename(dir: str) -> str:
    """
    Assuming a 'dir' is a directory filled solely with files sortable alphanumerically by date (something like
    "text_data_yyyymmdd.txt" or "yyyymmdd_params.json", returns the most recent file name.
    :param dir: string, directory in which all files are date sortable alphanumerically
    :return: string, file name for more recent file
    """
    return sorted(os.listdir(dir))[-1]


def get_dataset_file_suffix(sections):
    suffix = ''
    if 'title' in sections:
        suffix += 't'
    if 'abstract' in sections:
        suffix += 'a'

    return suffix


def get_last_experiment_number(results_dir: str) -> int:
    cur_exps = []
    for i in os.listdir(results_dir):
        try:
            cur_exps.append(int(i[:i.index('.')]))
        except ValueError:
            pass

    return sorted(cur_exps)[-1]
