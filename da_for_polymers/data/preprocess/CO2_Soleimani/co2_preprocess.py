import pkg_resources
import pandas as pd
import selfies as sf
from sklearn.preprocessing import OneHotEncoder
import ast

CO2_INVENTORY = pkg_resources.resource_filename(
    "da_for_polymers", "data/preprocess/CO2_Soleimani/co2_solubility_inventory.csv"
)

CO2_PREPROCESSED = pkg_resources.resource_filename(
    "da_for_polymers", "data/preprocess/CO2_Soleimani/co2_expt_data.csv"
)

CO2_OHE_PATH = pkg_resources.resource_filename(
    "da_for_polymers", "data/input_representation/CO2_Soleimani/ohe/master_ohe.csv"
)

AUTO_FRAG = pkg_resources.resource_filename(
    "da_for_polymers",
    "data/input_representation/CO2_Soleimani/automated_fragment/master_automated_fragment.csv",
)


class CO2_Solubility:
    """
    Class that contains functions to pre-process CO2 data.
    Ex. Add SMILES to experimental data
    """

    def __init__(self, co2_data, co2_inventory):
        self.data = pd.read_csv(co2_data)
        self.inventory = pd.read_csv(co2_inventory)

    def smi_match(self, co2_data_path):
        """
        Function that will match Polymer Label to appropriate SMILES to the Experimental CSV
        Args:
            co2_data_path: path to data with experimental results from CO2 solubility paper

        Returns:
            co2_expt_data.csv will have appropriate SMILES
        """
        # create dictionary of polymers w/ SMILES from inventory
        polymer_dict = {}
        for index, row in self.inventory.iterrows():
            polymer = self.inventory.at[index, "Polymer"]
            smi = self.inventory.at[index, "SMILES"]
            if polymer not in polymer_dict:
                polymer_dict[polymer] = smi

        # iterate through experimental data and input SMILES for polymer
        self.data["Polymer_SMILES"] = ""
        for index, row in self.data.iterrows():
            polymer = self.data.at[index, "Polymer"]
            self.data.at[index, "Polymer_SMILES"] = polymer_dict[polymer]

        self.data.to_csv(co2_data_path, index=False)

    def smi2selfies(self, co2_data_path):
        """
        Function that will match Polymer Label to appropriate SMILES to the Experimental CSV
        NOTE: assumes that .csv is already created with SMILES (must run smi_match first!)

        Args:
            co2_data_path: path to data with experimental results from CO2 solubility paper

        Returns:
            co2_expt_data.csv will have appropriate SELFIES
        """
        data = pd.read_csv(co2_data_path)
        data["Polymer_SELFIES"] = ""
        for index, row in data.iterrows():
            polymer_selfies = sf.encoder(row["Polymer_SMILES"])
            data.at[index, "Polymer_SELFIES"] = polymer_selfies

        data.to_csv(co2_data_path, index=False)

    def create_master_ohe(self, co2_expt_path: str, co2_ohe_path: str):
        """
        Generate a function that will one-hot encode the all of the polymer and solvent molecules. Each unique molecule has a unique number.
        Create one new column for the polymer and solvent one-hot encoded data.
        """
        master_df: pd.DataFrame = self.data
        polymer_ohe = OneHotEncoder()
        solvent_ohe = OneHotEncoder()
        polymer_ohe.fit(master_df["Polymer"].values.reshape(-1, 1))
        polymer_ohe_data = polymer_ohe.transform(
            master_df["Polymer"].values.reshape(-1, 1)
        )
        # print(f"{polymer_ohe_data=}")
        master_df["Polymer_ohe"] = polymer_ohe_data.toarray().tolist()
        # print(f"{master_df.head()}")
        # combine polymer and solvent ohe data into one column
        master_df.to_csv(co2_ohe_path, index=False)

    def bigsmiles_from_frag(self, automated_frag: str):
        """
        Function that takes ordered fragments (manually by hand) and converts it into BigSMILES representation, specifically block copolymers
        Args:
            automated_frag: path to data with automated fragmented polymers

        Returns:
            concatenates fragments into BigSMILES representation and returns to data
        """
        # polymer/mixture BigSMILES
        data = pd.read_csv(automated_frag)
        data["Polymer_BigSMILES"] = ""

        for index, row in data.iterrows():
            big_smi = "{[][<]"
            position = 0
            if len(ast.literal_eval(data["polymer_automated_frag"][index])) == 1:
                big_smi = ast.literal_eval(data["polymer_automated_frag"][index])[0]
            else:
                for frag in ast.literal_eval(data["polymer_automated_frag"][index]):
                    big_smi += str(frag)
                    if (
                        position
                        == len(ast.literal_eval(data["polymer_automated_frag"][index]))
                        - 1
                    ):
                        big_smi += "[>][]}"
                    else:
                        big_smi += "[>][<]}{[>][<]"
                    position += 1

            data.at[index, "Polymer_BigSMILES"] = big_smi

        data.to_csv(automated_frag, index=False)


# NOTE: BigSMILES is derived from manual fragments

preprocess = CO2_Solubility(CO2_PREPROCESSED, CO2_INVENTORY)
# preprocess.smi_match(CO2_PREPROCESSED)
# preprocess.smi2selfies(CO2_PREPROCESSED)
# preprocess.create_master_ohe(CO2_PREPROCESSED, CO2_OHE_PATH)
preprocess.bigsmiles_from_frag(AUTO_FRAG)
