import copy
import re
from collections import Counter
from typing import Union
import selfies as sf
import pandas as pd

import numpy as np

TOKENIZER_PATTERN = "(\%\([0-9]{3}\)|\[[^\]]+]|Se?|Si?|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\||\(|\)|\.|=|#|-|\+|\\|\/|:|~|@|\?|>>?|\*|\$|\%[0-9]{2}|[0-9])"
TOKENIZER_REGEX = re.compile(TOKENIZER_PATTERN)


class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, input):
        tokens = [t for t in TOKENIZER_REGEX.findall(input)]
        return ",".join(tokens)

    def pad_input(self, tokenized_array, seq_len):
        """Function that pads the reactions with 0 (_PAD) to a fixed length
        PRE-PADDING (features[ii, -len(review) :] = np.array(review)[:seq_len])
        POST-PADDING (features[ii, : len(review)] = np.array(review)[:seq_len])
        """
        features = np.zeros((len(tokenized_array), seq_len), dtype=int)
        for ii, review in enumerate(tokenized_array):
            if len(review) != 0:
                features[ii, : len(review)] = np.array(review)[:seq_len]
        return features.tolist()

    def tokenize_data(self, input_series):
        """Function that arranges series (pandas) of SMILES/BigSMILES/SELFIES and tokenizes each SMILES/BigSMILES/SELFIES.

        Parameter
        ----------
        input_series: a series of SMILES/BigSMILES/SELFIES from stepscore.csv

        Return
        -------
        tokenized_array: array of arrays of tokenized SMILES/BigSMILES/SELFIES for each SMILES/BigSMILES/SELFIES input
        """
        # tokenizing SMILES/BigSMILES/SELFIES
        input_dict = (
            Counter()
        )  # Dictionary that will map an atom to the number of times it appeared in all the training set
        tokenized_array = copy.copy(input_series)
        for i, reaction in enumerate(input_series):
            # The SMILES/BigSMILES/SELFIES will be stored as a list of tokens
            tokenized_array[i] = []
            tokenized_reaction = self.tokenize(reaction).split(",")
            for token in tokenized_reaction:  # tokenizing SMILES/BigSMILES/SELFIES
                input_dict.update([token])
                tokenized_array[i].append(token)
            if i % 50 == 0:
                print(str((i * 100) / len(tokenized_array)) + "% done")

        # organizing SMILES/BigSMILES/SELFIES dictionary
        # Sorting the atoms according to the number of appearances, with the most common atom being first
        input_dict = sorted(input_dict, key=input_dict.get, reverse=True)
        # Adding padding and unknown to our vocabulary so that they will be assigned an index
        input_dict = ["_UNK", "_PAD", "\\", "/"] + input_dict
        print(input_dict)

        # Dictionaries to store the token to index mappings and vice versa
        token2idx = {j: i for i, j in enumerate(input_dict)}
        # print("token2idx: ", token2idx)

        for i, reaction in enumerate(input_series):
            # Looking up the mapping dictionary and assigning the index to the respective reactions
            tokenized_array[i] = [
                token2idx[token] if token in token2idx else 0 for token in reaction
            ]
        max_length = 0
        for input_array in tokenized_array:
            if len(input_array) > max_length:
                max_length = len(input_array)
        print("Max sequence length: ", max_length)
        tokenized_array = self.pad_input(tokenized_array, max_length)
        vocab_length = len(input_dict)

        return tokenized_array, max_length, vocab_length, token2idx

    def tokenize_selfies(self, da_pair: pd.Series):
        """
        Function that returns max selfie length and unique selfie dictionary
        """
        selfie_dict = {"[nop]": 0, ".": 1}
        max_selfie_length = 1
        for pair in da_pair:
            selfie_alphabet = sorted(list(sf.get_alphabet_from_selfies([pair])))
            len_selfie = sf.len_selfies(pair)
            if len_selfie > max_selfie_length:
                max_selfie_length = len_selfie
            for char in selfie_alphabet:
                if char not in selfie_dict.keys():
                    selfie_dict[char] = len(selfie_dict)

        return selfie_dict, max_selfie_length

    def tokenize_from_dict(self, token2idx, input):
        """
        Function that tokenizes array of string representations with an existing dictionary
        * usually for test set
        """
        tokenized_input = self.tokenize(input).split(",")
        tokenized_list = [
            token2idx[token] if token in token2idx else 0 for token in tokenized_input
        ]

        return tokenized_list

    def build_token2idx(self, input_list):
        """Function that arranges list of SMILES/BigSMILES/SELFIES and builds dictionary.

        Parameter
        ----------
        input_list: a list of SMILES/BigSMILES/SELFIES

        Return
        -------
        token2idx: dictionary for all tokens seen in input_list
        """
        # tokenizing SMILES/BigSMILES/SELFIES
        input_dict = (
            Counter()
        )  # Dictionary that will map an atom to the number of times it appeared in all the training set
        tokenized_array = copy.copy(input_list)
        for i, reaction in enumerate(input_list):
            # The SMILES/BigSMILES/SELFIES will be stored as a list of tokens
            tokenized_array[i] = []
            tokenized_reaction = self.tokenize(reaction).split(",")
            for token in tokenized_reaction:  # tokenizing SMILES/BigSMILES/SELFIES
                input_dict.update([token])
                tokenized_array[i].append(token)
            if i % 50 == 0:
                print(str((i * 100) / len(tokenized_array)) + "% done")

        # organizing SMILES/BigSMILES/SELFIES dictionary
        # Sorting the atoms according to the number of appearances, with the most common atom being first
        input_dict = sorted(input_dict, key=input_dict.get, reverse=True)
        # Adding padding and unknown to our vocabulary so that they will be assigned an index
        input_dict = ["_PAD", "_UNK"] + input_dict

        # Dictionaries to store the token to index mappings and vice versa
        token2idx = {j: i for i, j in enumerate(input_dict)}

        return token2idx

    def tokenize_features(self, input_value: Union[int, float], token2idx: dict):
        """Tokenize numerical values into textual tokens.

        Args:
            input_value (Union[int, float]): numerical feature
            token2idx (dict): dictionary of one-hot encoding for complete vocabulary

        Returns:
            tokenized_feature (list[int]): list of tokens representing the feature.
        """
        # TODO: convert features to [0_0][._][5_-1][6_-2] = 0.56 tokens! -> do this in tokenizer
        # Return list of str and then list of ints.
        input_value: float = "{:.5f}".format(round(input_value, 5))
        # print(f"{input_value=}")
        input_value: str = str(input_value)
        property_tokenizer = PropertyTokenizer()
        tokenized_property: list[str] = property_tokenizer.tokenize(input_value)
        tokenized_feature: list[int] = []
        for token in tokenized_property:
            tokenized_feature.append(token2idx[token])

        return tokenized_feature


class PropertyTokenizer:
    """Run a property tokenization.
    Adapted from https://github.com/IBM/regression-transformer/blob/master/terminator/tokenization.py
    """

    def __init__(self):
        """Constructs a PropertyTokenizer."""
        self.regex = re.compile(r"\s*?(\+|-)?(\d+)(\.)?(\d+)?\s*")

    def tokenize(self, text: str):
        """Tokenization of a property.
        Args:
            text: text to tokenize.
        Returns:
            extracted tokens.
        """
        tokens = []
        matched = self.regex.match(text)
        if matched:
            sign, units, dot, decimals = matched.groups()
            tokens = []
            if sign:
                tokens += [f"_{sign}_"]
            tokens += [
                f"_{number}_{position}_" for position, number in enumerate(units[::-1])
            ][::-1]
            if dot:
                tokens += [f"_{dot}_"]
            if decimals:
                tokens += [
                    f"_{number}_-{position}_"
                    for position, number in enumerate(decimals, 1)
                ]
        return tokens


# for presentation (can be deleted)
# tk = Tokenizer()
# tokenized_smile = tk.tokenize(
#     "[C][C][S][C][=C][Branch2_1][Ring1][Ring2][C][S][C][Branch1_1][O][C][C][Branch1_1][Ring1][C][C][C][C][C][C][=C][C][Expl=Ring1][=N][C][C][=C][Branch2_1][Branch1_2][Branch1_2][C][=C][C][=C][Branch2_1][Branch1_1][O][C][S][C][Branch1_1][Branch2_1][C][=C][C][=C][S][Ring1][Branch1_1][=C][C][Expl=Ring1][Branch2_3][C][Branch2_1][Ring2][Branch1_2][C][=C][Branch1_1][O][C][C][Branch1_1][Ring1][C][C][C][C][C][C][S][C][Branch1_1][O][C][C][Branch1_1][Ring1][C][C][C][C][C][C][=C][Ring2][Ring1][Branch1_1][C][Ring2][Ring1][Branch2_2][=O][=O][S][Ring2][Ring2][Branch2_1][S][C][Expl=Ring2][Ring2][=N][C][Branch2_1][Ring1][Ring2][C][S][C][Branch1_1][O][C][C][Branch1_1][Ring1][C][C][C][C][C][C][=C][C][Expl=Ring1][=N][=C][Ring2][Branch1_2][O][C][Expl=Ring2][Branch1_2][=C]"
# )
# print(tokenized_smile)
