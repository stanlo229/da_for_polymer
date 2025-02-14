model_types=('RF' 'BRT' 'SVM')
for model in "${model_types[@]}"
do
    # AUGMENTED SMILES
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/augmented_SMILES/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/augmented_SMILES/StratifiedKFold/input_test_[0-9].csv --feature_names Augmented_SMILES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/Augmented_SMILES --random_state 22
    
    # # BRICS
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/BRICS/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/BRICS/StratifiedKFold/input_test_[0-9].csv --feature_names Polymer_BRICS,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/BRICS --random_state 22
    
    # # FINGERPRINT
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/fingerprint/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/fingerprint/StratifiedKFold/input_test_[0-9].csv --feature_names CO2_FP_radius_3_nbits_512,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/fingerprint --random_state 22
    
    # # AUTOMATED FRAG
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag --random_state 22
    
    # # AUTOMATED FRAG STR
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag_SMILES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag_SMILES --random_state 22
    
    # # AUGMENTED AUTOMATED FRAG
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag_aug,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag_aug --random_state 22
    
    # # AUGMENTED AUTOMATED FRAG STR
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag_aug_SMILES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag_aug_SMILES --random_state 22
    
    # # AUGMENTED AUTOMATED FRAG RECOMBINED SMILES
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag_aug_recombined_SMILES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag_aug_recombined_SMILES --random_state 22
    
    # # AUGMENTED AUTOMATED FRAG RECOMBINED FINGERPRINT
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/automated_fragment/StratifiedKFold/input_test_[0-9].csv --feature_names polymer_automated_frag_aug_recombined_fp,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/automated_frag_aug_recombined_fp --random_state 22
    
    # # DIMER FP
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_test_[0-9].csv --feature_names 2mer_fp,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/dimer_fp --random_state 22
    
    # # TRIMER FP
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_test_[0-9].csv --feature_names 3mer_fp,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/trimer_fp --random_state 22
    
    # # POLYMER GRAPH FP
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/circular_fingerprint/StratifiedKFold/input_test_[0-9].csv --feature_names 3mer_circular_graph_fp,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/polymer_graph_fp --random_state 22
    
    # # OHE
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/ohe/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/ohe/StratifiedKFold/input_test_[0-9].csv --feature_names Polymer_ohe,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/ohe --random_state 22
    
    #SMILES
    # python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/SMILES/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/SMILES/StratifiedKFold/input_test_[0-9].csv --feature_names Polymer_SMILES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/SMILES --random_state 22
    
    # SELFIES
    python ../train.py --train_path ../../../data/input_representation/CO2_Soleimani/SMILES/StratifiedKFold/input_train_[0-9].csv --test_path ../../../data/input_representation/CO2_Soleimani/SMILES/StratifiedKFold/input_test_[0-9].csv --feature_names Polymer_SELFIES,T_K,P_Mpa --target_name exp_CO2_sol_g_g --model_type "$model" --hyperparameter_optimization True --hyperparameter_space_path ./co2_hpo_space.json --results_path ../../../training/CO2_Soleimani/SELFIES --random_state 22
    
done