import os
import h5py
import numpy as np
import pandas as pd
from modisco.visualization.viz_sequence import plot_weights

# ------------- Extracting motifs from modisco results for visualisation----------------#
if not os.path.exists('../figures/MOTIFS/'):
    os.mkdir('../figures/MOTIFS/')


def get_predictive_pwms(mod_file, specie):
    print(specie)
    cwm = []
    motif_id = []
    strand = []
    metacluster_id = []
    n_motif_seqlets = []

    f = h5py.File(mod_file, "r")
    for metacluster_idx, metacluster_key in enumerate(f["metacluster_idx_to_submetacluster_results"]):
        metacluster = f["metacluster_idx_to_submetacluster_results"][metacluster_key]
        patterns = metacluster['seqlets_to_patterns_result']['patterns']
        print(metacluster_idx, metacluster_key, len(patterns['all_pattern_names']))

        for pattern_idx, pattern_name in enumerate(patterns['all_pattern_names']):
            pattern = patterns[pattern_name.decode()]
            pattern_seqlets = pattern["seqlets_and_alnmts"]["seqlets"]
            # add motif
            nfcwm = np.absolute(pattern["task0_contrib_scores"]["fwd"][:])
            nfcwm = len(pattern_seqlets) * (nfcwm / np.max(nfcwm.flat))
            cwm.append(nfcwm)
            motif_id.append(pattern_name.decode())
            metacluster_id.append(metacluster_key)
            n_motif_seqlets.append(len(pattern_seqlets))
            strand.append('fwd')
            save_fwd = f'../figures/MOTIFS/{specie}/{metacluster_key}_{pattern_name.decode()}_fwd.png'
            plot_weights(pattern["task0_contrib_scores"]["fwd"][:], save_fwd)


            # add motif reverse
            nrcwm = np.absolute(pattern["task0_contrib_scores"]["rev"][:])
            nrcwm = len(pattern_seqlets) * (nrcwm / np.max(nrcwm.flat))
            cwm.append(nrcwm)
            motif_id.append(pattern_name.decode())
            metacluster_id.append(metacluster_key)
            n_motif_seqlets.append(len(pattern_seqlets))
            strand.append('rev')
            save_fwd = f'../figures/MOTIFS/{specie}/{metacluster_key}_{pattern_name.decode()}_rev.png'
            plot_weights(pattern["task0_contrib_scores"]["rev"][:], save_fwd)

    # Save PFMs in H5 file
    cwm = np.array(cwm)
    motif_save = f'../figures/MOTIFS/{specie}/motifs.h5'
    os.system(f'rm -rf {motif_save}')
    h = h5py.File(motif_save, 'w')
    h.create_dataset('CWMs', data=cwm)
    h.close()
    meta_info = pd.DataFrame([motif_id, strand, metacluster_id, n_motif_seqlets]).T
    meta_info.columns = ['motifID', 'strand', 'metacluster', 'n_seqlets']
    meta_info.to_csv(f'../figures/MOTIFS/{specie}/meta_info.csv', sep='\t', index=False)


modisco_feats = ['arabidopsis_modisco.hdf5', 'zea_modisco.hdf5', 'solanum_modisco.hdf5', 'sbicolor_modisco.hdf5']
# For root, use
# modisco_feats = ['arabidopsis_modisco_root.hdf5', 'zea_modisco_root.hdf5', 'solanum_modisco_root.hdf5', 'sbicolor_modisco_root.hdf5']

species = ['AT', 'ZM', 'SL', 'SB']

for feats, sp in zip(modisco_feats, species):
    if not os.path.exists(f'../figures/MOTIFS/{sp}'):
        os.mkdir(f'../figures/MOTIFS/{sp}')
    feats_path = f'modisco/{feats}'
    get_predictive_pwms(feats_path, sp)
