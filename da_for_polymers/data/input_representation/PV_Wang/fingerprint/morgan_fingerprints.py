from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.DataStructs import cDataStructs
import pkg_resources
import pandas as pd
import numpy as np

PV_MASTER = pkg_resources.resource_filename(
    "da_for_polymers",
    "data/input_representation/PV_Wang/manual_frag/master_manual_frag.csv",
)

FP_PV = pkg_resources.resource_filename(
    "da_for_polymers",
    "data/input_representation/PV_Wang/fingerprint/pv_fingerprint.csv",
)

np.set_printoptions(threshold=np.inf)


class fp_data:
    """
    Class that contains functions to create fingerprints for OPV Data
    """

    def __init__(self, master_data):
        """
        Inits fp_data with preprocessed data

        Args:
            master_data: path to preprocessed data
        """
        self.master_data = pd.read_csv(master_data)

    def create_master_fp(self, fp_path, radius: int, nbits: int):
        """
        Create and export dataframe with fingerprint bit vector representations to .csv or .pkl file

        Args:
            fp_path: path to master fingerprint data for training
            radius: radius for creating fingerprints
            nbits: number of bits to create the fingerprints

        Returns:
            new dataframe with fingerprint data for training
        """
        fp_df = self.master_data

        # Only used when first creating dataframe from master data before
        # fp_df.drop(
        #     [
        #         "Polymer_BigSMILES",
        #         "Polymer_SELFIES",
        #         "Solvent_SELFIES",
        #         "PS_manual_tokenized",
        #         "SP_manual_tokenized",
        #         "PS_manual_tokenized_aug",
        #         "SP_manual_tokenized_aug",
        #     ],
        #     axis=1,
        # )

        new_column_pm_pair = "PS_FP" + "_radius_" + str(radius) + "_nbits_" + str(nbits)
        fp_df[new_column_pm_pair] = " "
        for index, row in fp_df.iterrows():
            p_mol = Chem.MolFromSmiles(fp_df.at[index, "Polymer_SMILES"])
            bitvector_p = AllChem.GetMorganFingerprintAsBitVect(
                p_mol, radius, nBits=nbits
            )
            fp_p = list(bitvector_p)
            s_mol = Chem.MolFromSmiles(fp_df.at[index, "Solvent_SMILES"])
            bitvector_s = AllChem.GetMorganFingerprintAsBitVect(
                s_mol, radius, nBits=nbits
            )
            fp_s = list(bitvector_s)
            fp_p.extend(fp_s)
            fp_ps = fp_p

            fp_df.at[index, new_column_pm_pair] = fp_ps

        fp_df.to_csv(fp_path, index=False)
        # fp_df.to_pickle(fp_path)


fp_master = fp_data(PV_MASTER)  # replace with FP_PV after first run
fp_master.create_master_fp(FP_PV, 3, 512)
