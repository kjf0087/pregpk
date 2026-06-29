from typing import Any
import warnings
import pandas as pd


def add_dict_to_df_using_reference_column(df: pd.DataFrame, data: dict, ref_col: Any, new_col: Any, default: Any=None,
                                          override_existing: bool=False) -> pd.DataFrame:
    """
    Adds data from a dictionary to a current DataFrame, where the row in which the data is added is chosen by
    referencing an existing column in the DataFrame (which should contain unique values).
    :param df: pandas.DataFrame with current data
    :param data: dictionary containing data to be added to df
    :param ref_col: name column of df whose values will be used to define where data will be added
    :param new_col: name of new column where data will be added
    :param default: Any, default value of data if value in ref_col is not found in data.keys()
    :param override_existing: bool, whether value in new_col should be overwritten if it currently exists
    :return: pandas.DataFrame with new_col.
    """
    if new_col in df.columns:
        if not override_existing:
            warnings.warn(f'DataFrame already contained column {new_col}. If you want to override current values,'
                          f'set override_existing to True.')
            return df

    ref_vals = set(df[ref_col].tolist())
    new_vals = data.keys()
    n_shared_vals = len(set(ref_vals) & set(new_vals))
    if len(ref_vals) > n_shared_vals:
        warnings.warn(f"{len(ref_vals) - n_shared_vals} rows of column {ref_col} do not have counterparts as keys in "
                      f"updating dictionary, and thus will not be updated")
    if len(new_vals) > n_shared_vals:
        warnings.warn(f"{len(new_vals) - n_shared_vals} keys in updating dictionary dont have matches in {ref_col} of "
                      f"DataFrame, and thus won't be added.")

    for idx, row in df.iterrows():
        ref_val = row[ref_col]
        if ref_val in data:
            df.at[idx, new_col] = data[ref_val]
        else:
            df.at[idx, new_col] = default

    return df


def filter_text_df(text_df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes rows of data that don't meet requirements to be used in automated publication selection testing.
    """
    not_reviewed = text_df.index[~text_df['been_reviewed']].tolist()  # Articles not reviewed by Emily
    is_review_art = text_df.index[text_df['is_review']].tolist()  # Review articles
    not_english = text_df.index[~text_df['is_english']].tolist()  # Non-english articles
    remove = list(set(not_reviewed + is_review_art + not_english))

    print(f'Removing:\n'
          f'\t{len(not_reviewed)} publications as they have not been reviewed by Emily\n'
          f'\t{len(is_review_art)} publications as they are review articles\n'
          f'\t{len(not_english)} publications as they are not in English\n'
          f'\t{len(remove)} publications in total\n')

    text_df = text_df.drop(remove, axis=0)

    return text_df
