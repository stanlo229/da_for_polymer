import ast
import json
from multiprocessing.sharedctypes import Value
from tokenize import Token
from typing import Tuple, Union
import pandas as pd
import numpy as np
from xgboost import train

from da_for_polymers.ML_models.sklearn.tokenizer import Tokenizer

np.set_printoptions(suppress=True)


def tokenize_from_dict(token2idx: dict, input_value: Union[list, str]) -> list:
    """

    Args:
        token2idx (dict): dictionary of unique tokens with corresponding indices.
        input_value (list, str): input_value with tokens that match the token2idx.

    Returns:
        tokenized_list (list): list of tokenized inputs
    """
    tokenized_list: list = []
    for token in input_value:
        tokenized_list.append(token2idx[token])

    return tokenized_list


def pad_input(input_list_of_list: list, max_input_length: int) -> list:
    """Pad the input_value (pre-padding) with 0's until max_length is met.

    Args:
        input_list_of_list (list): list of inputs.
        max_length (int): max length of any input_value in the entire dataset.

    Returns:
        input_list_of_list (list): list of inputs with pre-padding.
    """
    for input_list in input_list_of_list:
        for i in range(max_input_length - len(input_list)):
            input_list.insert(0, 0)

    return input_list_of_list


def feature_scale(feature_series: pd.Series) -> Union[float, float]:
    """
    Min-max scaling of a feature.
    Args:
        feature_series: a pd.Series of a feature
    Returns:
        scaled_feature: a np.array (same index) of feature that is min-max scaled
        max_value: maximum value from the entire feature array
    """
    feature_array: np.ndarray = feature_series.to_numpy().astype("float64")
    max_value: float = np.nanmax(feature_array)
    min_value: float = np.nanmin(feature_array)
    return max_value, min_value


# TODO: return max length for fragments and fingerprints! not only SMILES, etc.
def process_features(
    train_feature_df, test_feature_df, token2idx_path: str
) -> Tuple[np.ndarray, np.ndarray]:
    """Processes various types of features (str, float, list) and returns "training ready" arrays.

    Args:
        train_feature_df (pd.DataFrame): subset of train_df with selected features.
        test_feature_df (pd.DataFrame): subset of test_df with selected features.

    Returns:
        input_train_array (np.array): tokenized, padded array ready for training
        input_test_array (np.array): tokenized, padded array ready for validation
    """
    assert len(train_feature_df) > 1, train_feature_df
    assert len(test_feature_df) > 1, test_feature_df
    # Cannot have more than 1 input_value representation, so the only str type value will be the input_value representation.
    column_headers: list = train_feature_df.columns
    for column in column_headers:
        if type(train_feature_df[column][1]) == str:
            input_representation: str = column

    # calculate feature dict
    feature_scale_dict: dict = {}
    concat_df: pd.DataFrame = pd.concat(
        [train_feature_df, test_feature_df], ignore_index=True
    )
    for column in column_headers:
        if any(
            [
                isinstance(concat_df[column][1], np.float64),
                isinstance(concat_df[column][1], float),
                isinstance(concat_df[column][1], np.int64),
                isinstance(concat_df[column][1], int),
            ]
        ):
            feature_max, feature_min = feature_scale(concat_df[column])
            feature_column_max = column + "_max"
            feature_column_min = column + "_min"
            feature_scale_dict[feature_column_max] = feature_max
            feature_scale_dict[feature_column_min] = feature_min

    # TOKENIZATION
    # must loop through entire dataframe for token2idx
    input_instance = None
    try:
        input_value = ast.literal_eval(concat_df[input_representation][1])
        if isinstance(input_value[0], list):
            input_instance = "list_of_list"
            # print("input_value is a list of list")
        else:
            input_instance = "list"
            # print("input_value is a list which could be: 1) fragments or 2) SMILES")
    except:  # The input_value was not a list, so ast.literal_eval will raise ValueError.
        input_instance = "str"
        input_value = concat_df[input_representation][1]
        # print("input_value is a string")
    print(input_instance)
    if (
        input_instance == "list"
    ):  # could be list of fragments or list of (augmented) SMILES.
        # check if list of: 1) fragments or 2) SMILES
        if "Augmented" in input_representation or "aug_SMILES" in input_representation:
            augmented_smi_list: list = []
            for index, row in concat_df.iterrows():
                input_value = ast.literal_eval(row[input_representation])
                for aug_value in input_value:
                    augmented_smi_list.append(aug_value)
            augmented_smi_series: pd.Series = pd.Series(augmented_smi_list)
            (
                tokenized_array,
                max_length,
                vocab_length,
                token2idx,
            ) = Tokenizer().tokenize_data(augmented_smi_series)
        else:
            token2idx: dict = {"_PAD": 0}
            token_idx = len(token2idx)
            for index, row in concat_df.iterrows():
                input_value = ast.literal_eval(row[input_representation])
                for frag in input_value:
                    if frag not in list(token2idx.keys()):
                        token2idx[frag] = token_idx
                        token_idx += 1
    elif (
        input_instance == "list_of_list"
    ):  # list of list of augmented fragments or augmented fingerprints
        token2idx: dict = {"_PAD": 0}
        token_idx = len(token2idx)
        for index, row in concat_df.iterrows():
            input_value = ast.literal_eval(row[input_representation])
            for aug_value in input_value:
                for frag in aug_value:
                    if frag not in list(token2idx.keys()):
                        token2idx[frag] = token_idx
                        token_idx += 1
    elif input_instance == "str":
        if (
            "smiles" in input_representation
            or "SMILES" in input_representation
            or "SELFIES" in input_representation
            or "selfies" in input_representation
        ):
            (
                tokenized_array,
                max_length,
                vocab_length,
                token2idx,
            ) = Tokenizer().tokenize_data(concat_df[input_representation])
        elif "selfies" in input_representation:
            token2idx, vocab_length = Tokenizer().tokenize_selfies(
                concat_df[input_representation]
            )
    else:
        raise TypeError("input_value is neither str or list. Fix it!")
    # print(f"{token2idx=}")
    max_input_length = 0  # for padding
    # processing training data
    input_train_list = []
    for index, row in train_feature_df.iterrows():
        # augmented data needs to be processed differently.
        if any(
            [
                "Augmented" in input_representation,
                "aug_SMILES" in input_representation,
                input_instance == "list_of_list",
            ]
        ):
            # get feature variables (not the input representation)
            feature_list = []
            for column in column_headers:
                try:
                    input_value = ast.literal_eval(row[column])
                except:
                    input_value = row[column]
                if any(
                    [
                        isinstance(input_value, np.float64),
                        isinstance(input_value, float),
                        isinstance(input_value, np.int64),
                        isinstance(input_value, int),
                    ]
                ):
                    # feature scaling (min-max)
                    input_value = row[column]
                    column_max = column + "_max"
                    column_min = column + "_min"
                    input_column_max = feature_scale_dict[column_max]
                    input_column_min = feature_scale_dict[column_min]
                    input_value = (input_value - input_column_min) / (
                        input_column_max - input_column_min
                    )
                    feature_list.append(input_value)
            # process augmented input representations
            input_value = ast.literal_eval(row[input_representation])
            for aug_value in input_value:
                tokenized_list = []
                if (
                    "Augmented" in input_representation
                    or "aug_SMILES" in input_representation
                ):
                    tokenized_list.extend(
                        Tokenizer().tokenize_from_dict(token2idx, aug_value)
                    )  # SMILES
                else:
                    tokenized_list.extend(
                        tokenize_from_dict(token2idx, aug_value)
                    )  # fragments
                tokenized_list.extend(feature_list)
                input_train_list.append(tokenized_list)
                if len(tokenized_list) > max_input_length:  # for padding
                    max_input_length = len(tokenized_list)

        else:
            tokenized_list = []
            for column in column_headers:
                # input_value type can be (list, str, float, int)
                try:
                    input_value = ast.literal_eval(row[column])
                except:
                    input_value = row[column]
                # tokenization
                if isinstance(input_value, list):
                    input_value = ast.literal_eval(row[column])
                    tokenized_list.extend(
                        tokenize_from_dict(token2idx, input_value)
                    )  # fragments
                elif isinstance(input_value, str):
                    input_value = row[column]
                    tokenized_list.extend(
                        Tokenizer().tokenize_from_dict(token2idx, input_value)
                    )  # SMILES
                elif any(
                    [
                        isinstance(input_value, np.float64),
                        isinstance(input_value, float),
                        isinstance(input_value, np.int64),
                        isinstance(input_value, int),
                    ]
                ):
                    # feature scaling (min-max)
                    input_value = row[column]
                    column_max = column + "_max"
                    column_min = column + "_min"
                    input_column_max = feature_scale_dict[column_max]
                    input_column_min = feature_scale_dict[column_min]
                    input_value = (input_value - input_column_min) / (
                        input_column_max - input_column_min
                    )
                    tokenized_list.extend([input_value])
                else:
                    print(type(input_value))
                    raise ValueError("Missing value. Cannot be null value in dataset!")
            if len(tokenized_list) > max_input_length:  # for padding
                max_input_length = len(tokenized_list)

            input_train_list.append(tokenized_list)

    # processing validation data
    input_test_list = []
    for index, row in test_feature_df.iterrows():
        # augmented data needs to be processed differently.
        if any(
            [
                "Augmented" in input_representation,
                "aug_SMILES" in input_representation,
                input_instance == "list_of_list",
            ]
        ):
            # get feature variables (not the input representation)
            feature_list = []
            for column in column_headers:
                try:
                    input_value = ast.literal_eval(row[column])
                except:
                    input_value = row[column]
                if any(
                    [
                        isinstance(input_value, np.float64),
                        isinstance(input_value, float),
                        isinstance(input_value, np.int64),
                        isinstance(input_value, int),
                    ]
                ):
                    # feature scaling (min-max)
                    input_value = row[column]
                    column_max = column + "_max"
                    column_min = column + "_min"
                    input_column_max = feature_scale_dict[column_max]
                    input_column_min = feature_scale_dict[column_min]
                    input_value = (input_value - input_column_min) / (
                        input_column_max - input_column_min
                    )
                    feature_list.append(input_value)
            # process augmented input representations
            input_value = ast.literal_eval(row[input_representation])
            # NOTE: In the validation set, only the first augmented value is taken. We do not want to perform predictions on augmented data.
            aug_value = input_value[0]
            tokenized_list = []
            if (
                "Augmented" in input_representation
                or "aug_SMILES" in input_representation
            ):
                tokenized_list.extend(
                    Tokenizer().tokenize_from_dict(token2idx, aug_value)
                )  # SMILES
            else:
                tokenized_list.extend(
                    tokenize_from_dict(token2idx, aug_value)
                )  # fragments
            tokenized_list.extend(feature_list)
            input_test_list.append(tokenized_list)
            if len(tokenized_list) > max_input_length:  # for padding
                max_input_length = len(tokenized_list)

        else:
            tokenized_list = []
            for column in column_headers:
                # input_value type can be (list, str, float, int)
                try:
                    input_value = ast.literal_eval(row[column])
                except:
                    input_value = row[column]
                # tokenization
                if isinstance(input_value, list):
                    input_value = ast.literal_eval(row[column])
                    tokenized_list.extend(
                        tokenize_from_dict(token2idx, input_value)
                    )  # fragments
                elif isinstance(input_value, str):
                    input_value = row[column]
                    tokenized_list.extend(
                        Tokenizer().tokenize_from_dict(token2idx, input_value)
                    )  # SMILES
                elif any(
                    [
                        isinstance(input_value, np.float64),
                        isinstance(input_value, float),
                        isinstance(input_value, np.int64),
                        isinstance(input_value, int),
                    ]
                ):
                    # feature scaling (min-max)
                    input_value = row[column]
                    column_max = column + "_max"
                    column_min = column + "_min"
                    input_column_max = feature_scale_dict[column_max]
                    input_column_min = feature_scale_dict[column_min]
                    input_value = (input_value - input_column_min) / (
                        input_column_max - input_column_min
                    )
                    tokenized_list.extend([input_value])
                else:
                    print(type(input_value))
                    raise ValueError("Missing value. Cannot be null value in dataset!")
            if len(tokenized_list) > max_input_length:  # for padding
                max_input_length = len(tokenized_list)

            input_test_list.append(tokenized_list)

    # padding
    input_train_list = pad_input(input_train_list, max_input_length)
    input_test_list = pad_input(input_test_list, max_input_length)
    input_train_array = np.array(input_train_list)
    input_test_array = np.array(input_test_list)
    assert type(input_train_array[0]) == np.ndarray, input_train_array
    assert type(input_test_array[0]) == np.ndarray, input_test_array
    # export token2idx
    with open(token2idx_path, "w") as handle:
        json.dump(token2idx, handle, indent=2)

    return input_train_array, input_test_array, max_input_length


def process_target(
    train_target_df, test_target_df
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """Processes one target value through the following steps:
    1) min-max scaling
    2) return as array

    Args:
        train_target_df (pd.DataFrame): target values for training dataframe
        test_target_df (pd.DataFrame): target values for validation dataframe
    Returns:
        target_train_array (np.array): array of training targets
        target_test_array (np.array): array of validation targets
        target_max (float): maximum value in dataset
        target_min (float): minimum value in dataset
    """
    assert len(train_target_df) > 1, train_target_df
    assert len(test_target_df) > 1, test_target_df
    concat_df = pd.concat([train_target_df, test_target_df], ignore_index=True)
    # first column will always be the target column
    target_max, target_min = feature_scale(train_target_df[train_target_df.columns[0]])

    # Cannot have more than 1 input_value representation, so the only str type value will be the input_value representation.
    column_headers = train_target_df.columns
    for column in column_headers:
        if type(train_target_df[column][1]) == str:
            input_representation = column

    # additional data points for targets if data is augmented
    input_instance = None
    try:
        input_value = ast.literal_eval(concat_df[input_representation][1])
        if isinstance(input_value[0], list):
            input_instance = "list_of_list"
            # print("input_value is a list of list")
        else:
            input_instance = "list"
            # print("input_value is a list which could be: 1) fragments or 2) SMILES")
    except:  # The input_value was not a list, so ast.literal_eval will raise ValueError.
        input_instance = "str"
        # print("input_value is a string")

    # duplicate number of target values with the number of augmented data points
    if any(
        [
            "Augmented" in input_representation,
            "aug_SMILES" in input_representation,
            input_instance == "list_of_list",
        ]
    ):
        target_train_list = []
        for index, row in train_target_df.iterrows():
            input_value = ast.literal_eval(row[input_representation])
            for i in range(len(input_value)):
                target_train_list.append(row[train_target_df.columns[0]])

        target_test_list = []
        for index, row in test_target_df.iterrows():
            input_value = ast.literal_eval(row[input_representation])
            # NOTE: In the validation set, only the first augmented value is taken. We do not want to perform predictions on augmented data.
            target_test_list.append(row[test_target_df.columns[0]])

        target_train_array = np.array(target_train_list)
        target_test_array = np.array(target_test_list)
    else:
        target_train_array = train_target_df[train_target_df.columns[0]].to_numpy()
        target_train_array = np.ravel(target_train_array)
        target_test_array = test_target_df[test_target_df.columns[0]].to_numpy()
        target_test_array = np.ravel(target_test_array)

    target_train_array = (target_train_array - target_min) / (target_max - target_min)
    target_test_array = (target_test_array - target_min) / (target_max - target_min)

    return target_train_array, target_test_array, target_max, target_min


def get_space_dict(space_json_path, model_type):
    """Opens json file and returns a dictionary of the space.

    Args:
        space_json_path (str): filepath to json containing search space of hyperparameters

    Returns:
        space (dict): dictionary of necessary hyperparameters
    """
    space = {}
    with open(space_json_path) as json_file:
        space_json = json.load(json_file)
    if model_type == "RF":
        space_keys = [
            "n_estimators",
            "min_samples_leaf",
            "min_samples_split",
            "max_depth",
        ]
    elif model_type == "BRT":
        space_keys = [
            "alpha",
            "n_estimators",
            "max_depth",
            "subsample",
            "min_child_weight",
        ]
    elif model_type == "KRR":
        pass
    elif model_type == "LR":
        pass
    elif model_type == "SVM":
        space_keys = ["kernel", "degree"]
    for key in space_keys:
        assert key in space_json.keys(), key
        space[key] = space_json[key]

    return space


# l = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
# l2 = [[1, 2, 3], [3, 4, 5], [2, 3]]

# print(np.array(l)[0], type(np.array(l)[0]))
