#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 10:56:15 2020

@author: ibarlow
"""

import h5py
from pathlib import Path
import pandas as pd

annotations_file = Path('/Volumes/Ashur Pro2/PrestwickScreen/AuxiliaryFiles/20201201/PrestwickScreen_20201214_130030_wells_annotations.hdf5')
update_wdir=False
#%%
if __name__ == "__main__":
    if update_wdir:
        with h5py.File(annotations_file, 'r+') as fid:
            fid["/filenames_df"].attrs["working_dir"] = str('/Volumes/Ashur Pro2/PrestwickScreen/MaskedVideos/20201127')
            

    with pd.HDFStore(annotations_file) as fid:    
        annotated_files = fid['/filenames_df']
        well_annotations = fid['/wells_annotations_df']
        wdir = fid.get_storer('/filenames_df').attrs.working_dir 


    prestim_files = list(
        Path(str(annotations_file.parent).replace('AuxiliaryFiles',
                                   'MaskedVideos')).rglob('metadata.hdf5')
        )
    
    # if annotated_files.shape[0] ==len(prestim_files):
    #     continue
        
    prestim_files = [Path(f) for f in prestim_files if 'prestim' in str(f)]
    prestim_files = ['{}/{}'.format(f.parent.name, f.name)
                     for f in prestim_files] 
        
    missing_files = set(prestim_files).symmetric_difference(annotated_files['filename'])
    print(missing_files)
    
    #remove these files
    files_to_drop = list(annotated_files.query('@missing_files in filename').file_id)
    
    annotated_files.drop(index=annotated_files.query('@files_to_drop in file_id').index,
                         inplace=True)
    well_annotations.drop(index=well_annotations.query('@files_to_drop in file_id').index,
                          inplace=True)
    # annotated_files.reset_index(drop=True, inplace=True)
    # annotated_files['file_id'] = annotated_files.index
    
   
    with pd.HDFStore(annotations_file, 'r+') as fid:

        annotated_files.to_hdf(
            fid,
            key='/filenames_df',
            index=False,
            mode='r+')  

        well_annotations.to_hdf(
            fid,
            key='/wells_annotations_df',
            index=False,
            mode='r+')   
              
        
    with h5py.File(annotations_file, 'r+') as fid:
        fid["/filenames_df"].attrs["working_dir"] = str(wdir)         
        # print(update)
        # wdir = fid.get_storer('/filenames_df').attrs.working_dir             
        