"""
Python file that contains functions and classes which inputs a total dataset, and returns
the corresponding train, and validation set. 
"""
import os
import pandas as pd
from pathlib import Path

from sklearn.model_selection import KFold, StratifiedKFold


def main(config):
    """
    Produces cross-validation folds for any training data.

    Args:
        config (dict): Configuration paths and parameters.

    Returns:
        input_train_fold_*: Examples from dataset used for training, created in current directory.
        input_test_fold_*: Examples from dataset used for testing, created in current directory.
    """
    dataset_dir = Path(config["dataset_path"])
    data_df = pd.read_csv(config["dataset_path"])
    num_of_folds = config["num_of_folds"]
    seed = config["random_seed"]
    if config["type_of_crossval"] == "KFold":
        fold_path = dataset_dir.parent / Path(config["type_of_crossval"] + "/")
        fold_path.mkdir(parents=True, exist_ok=True)
        kf = KFold(n_splits=num_of_folds, shuffle=True, random_state=seed)
        i = 0
        for train_index, test_index in kf.split(data_df):
            train = data_df.iloc[train_index]
            test = data_df.iloc[test_index]
            train_dir = fold_path / f"input_train_{i}.csv"
            test_dir = fold_path / f"input_test_{i}.csv"
            train.to_csv(train_dir, index=False)
            test.to_csv(test_dir, index=False)
            i += 1

    elif config["type_of_crossval"] == "StratifiedKFold":
        fold_path = dataset_dir.parent / Path(config["type_of_crossval"] + "/")
        fold_path.mkdir(parents=True, exist_ok=True)
        kf = StratifiedKFold(n_splits=num_of_folds, shuffle=True, random_state=seed)
        i = 0
        for train_index, test_index in kf.split(
            data_df, data_df[config["stratified_label"]]
        ):
            train = data_df.iloc[train_index]
            test = data_df.iloc[test_index]
            train_dir = fold_path / f"input_train_{i}.csv"
            test_dir = fold_path / f"input_test_{i}.csv"
            train.to_csv(train_dir, index=False)
            test.to_csv(test_dir, index=False)
            i += 1
    else:
        raise ValueError(
            "Wrong KFold operation. Choose between KFold or StratifiedKFold."
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "--dataset_path",
        type=str,
        help="Absolute filepath to complete dataset for cross-validation",
    )
    parser.add_argument(
        "--num_of_folds",
        type=int,
        help="Number of folds to create for cross-validation",
    )
    parser.add_argument(
        "--type_of_crossval",
        type=str,
        default="KFold",
        help="Select between KFold and StratifiedKFold",
    )
    parser.add_argument(
        "--stratified_label",
        type=str,
        help="If StratifiedKFold is selected, it is necessary.",
    )
    parser.add_argument(
        "--random_seed",
        type=int,
        default=22,
        help="Random seed initialization to ensure folds are consistent.",
    )
    args = parser.parse_args()
    config = vars(args)
    main(config)

### EXAMPLE USE
"""
python ../../cross_validation.py --dataset_path ~/Research/Repos/da_for_polymers/da_for_polymers/data/input_representation/PV_Wang/SMILES/MASTER_Smiles.csv --num_of_folds 5 --type_of_crossval StratifiedKFold --stratified_label Solvent

python ../../cross_validation.py --dataset_path ~/Research/Repos/da_for_polymers/da_for_polymers/data/input_representation/CO2_Soleimani/augmented_SMILES/train_aug_master.csv --num_of_folds 7 --type_of_crossval StratifiedKFold --stratified_label Polymer
"""
