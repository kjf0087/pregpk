from typing import Any


def split_list(init_list: list, split_size: int) -> list:
    """
    Splits a list into a nested list where each sublist is of maximum size split_size. If init_list is not evenly
    divisible by split_size, the last element of the returned list will be of the remaining size.
    :param init_list: list to split into nested list
    :param split_size: size of each list in returned split list
    :return: nested list where each element has size split_size (or smaller, in case of last element)
    """
    return [init_list[i:i+split_size] for i in range(0, len(init_list), split_size)]


def nested_keys_exists(element: dict, *keys: Any) -> bool:
    """
    Check if *keys (nested) exists in `element` (dict). From StackOverflow (by Arount).
    :param element: variable (should be dict) in which to check whether the nested keys exist
    :param keys: one or more keys, in order from least to most nested (outwards in)
    :return: boolean, True if nested keys exist in element, False otherwise.
    """

    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def comma_sep_str_from_list(pmid_list:list) -> str:
    """
    Converts a list of PubMed IDs to a single string with PMIDs delimited by commas, useful for API requests.
    :param pmid_list: list with PubMed IDs (PMIDs)
    :return: single string combining each PMID
    """
    return ','.join(map(str, pmid_list))


def convert_to_python_obj(obj: Any) -> Any:
    """
    Converts a non-python native object which is an instance of a python object (string, list, dict, etc.) to a
    python-native type.
    :param obj: Any type, but must be an instance of a python-native object (bool, str, int, list, etc.)
    :return: Python-native object version of inputted object.
    """
    if isinstance(obj, bool):
        obj = convert_to_python_bool(obj)
    elif isinstance(obj, str):
        obj = convert_to_python_str(obj)
    elif isinstance(obj, int):
        obj = convert_to_python_int(obj)
    elif isinstance(obj, dict):
        obj = convert_to_python_dict(obj)
    elif isinstance(obj, list):
        obj = convert_to_python_list(obj)
    elif isinstance(obj, tuple):
        obj = convert_to_python_tuple(obj)

    return obj


def convert_to_python_bool(obj):
    """
    Converts non-python native boolean instance to python-native one.
    :param obj: object where type is an instance of bool
    :return: python native bool
    """
    return bool(obj)


def convert_to_python_str(obj):
    """
    Converts non-python native string instance to python-native one.
    :param obj: object where type is an instance of str
    :return: python native str
    """
    return str(obj)


def convert_to_python_int(obj):
    """
    Converts non-python native integer instance to python-native one.
    :param obj: object where type is an instance of int
    :return: python native str
    """
    return int(obj)


def convert_to_python_dict(obj):
    """
    Converts non-python native dict instance to python-native one.
    :param obj: object where type is an instance of dict
    :return: python native dict
    """
    return {convert_to_python_obj(key): convert_to_python_obj(val) for key, val in obj.items()}


def convert_to_python_list(obj):
    """
    Converts non-python native list instance to python-native one.
    :param obj: object where type is an instance of list
    :return: python native list
    """
    return [convert_to_python_obj(i) for i in obj]


def convert_to_python_tuple(obj):
    """
    Converts non-python native tuple instance to python-native one.
    :param obj: object where type is an instance of tuple
    :return: python native tuple
    """
    return (convert_to_python_obj(i) for i in obj)

