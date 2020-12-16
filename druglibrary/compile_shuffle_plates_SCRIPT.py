#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 12:08:03 2020

@author: ibarlow

Script for making the shuffled prestwick library plates

For each robot run:
    - robot runlog
    - source slot
    - drug type

"""
import pandas as pd
from pathlib import Path
from tierpsytools.hydra.compile_metadata import merge_robot_metadata
import warnings

ROOT_DIR = Path('/Users/ibarlow/OneDrive - Imperial College London/Documents/behavgenom_copy/PrestwickScreen')

PREPROCESSING_REQUIRED = False
SOURCEPLATE_FILES = list(
            ROOT_DIR.rglob('*sourceplates.csv*'))
SOURCEPLATE_FILES = [i for i in SOURCEPLATE_FILES if 'shuffled' not in str(i)]

DSLOT_RUN_NUMBER_DICT = {11:1,
                   8:2,
                   9:3,
                   5:4}

def update_sourceplate_files(sourceplate_files):
    for file in sourceplate_files:
        splate = pd.read_csv(file)
        splate.loc[:, 'robot_runlog_filename'] = splate['robot_runlog_filename'].apply(lambda x: x.replace('runlog.csv',
                                                                  'runlog_clean.csv'))

        warnings.warn('{} file being edited to update robot log'.format(file))
        splate.to_csv(file, index=False)
    return
 

def preprocess_runlogs(runlogs):
        
    for count, file in enumerate(runlogs):
        rlog = pd.read_csv(file,
                           skiprows=4)
        rlog = rlog.drop(rlog[
                rlog['source_slot'] == rlog['destination_slot']
                ].index)
        rlog.to_csv(file.parent / (file.stem + '_clean.csv'), index=False)
    
    return

#%%
if __name__ == '__main__':
    if PREPROCESSING_REQUIRED == True:
        robot_logs = list(ROOT_DIR.rglob('*runlog.csv'))
        
        preprocess_runlogs(robot_logs)
        update_sourceplate_files(SOURCEPLATE_FILES)
 #%%       
    for file in SOURCEPLATE_FILES:
        robot_metadata = merge_robot_metadata(file,
                                              saveto=None,
                                              del_if_exists=True,
                                              compact_drug_plate=True,
                                              drug_by_column=False)
        robot_metadata.sort_values(by=['source_plate_number',
                                       'destination_well'],
                                   ignore_index=True,
                                   inplace=True)
        robot_metadata['robot_run_number'] = robot_metadata.destination_slot.map(DSLOT_RUN_NUMBER_DICT)
        
        # add in the unshuffled plate a plate 4
        _p04 = pd.read_csv(file)
        _p04['robot_run_number'] = 4
        _p04.rename(columns={'source_well':'destination_well'},
                    inplace=True)
        robot_metadata = pd.concat([robot_metadata, _p04], axis=0)
        
        robot_metadata['shuffled_plate_id'] = [r.source_plate_id +
                                               '_sh%02d' %(r.robot_run_number)
                                               for i, r in
                                               robot_metadata.iterrows()]
        robot_metadata['is_bad_well'].fillna(False, inplace=True)
        
        robot_metadata.sort_values(by=['shuffled_plate_id',
                                       'destination_well'],
                                   inplace=True)
        robot_metadata.to_csv(str(file).replace('.csv', '_shuffled.csv'),
                              index=False)
        # del robot_metadata