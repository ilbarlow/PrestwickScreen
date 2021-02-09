#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 16:11:07 2020

@author: ibarlow

script to find which files are missing from my hard drive
"""

from pathlib import Path
import pandas as pd
from tierpsytools.hydra.hydra_filenames_helper import find_imgstore_videos, raw_to_masked, raw_to_featuresN
import datetime

HD_DIR = Path('/Volumes/Ashur Pro2/PrestwickScreen')
BEHAV_DIR = Path('/Volumes/behavgenom$/Ida/Data/Hydra/PrestwickScreen')

check_bgenom=True

#%%
def check_masked_results(df):
    df['masked_vid'] = df.full_path.apply(raw_to_masked)
    df['missing_masked'] = df.masked_vid.apply(lambda x: not x.exists())
    df['results'] = df.full_path.apply(raw_to_featuresN)
    df['missing_results'] = df.results.apply(lambda x: not x.exists())
    return df

#%%
if __name__ == '__main__':
    if check_bgenom:
        df = find_imgstore_videos(BEHAV_DIR)
        behav_genom_df = check_masked_results(df)
        behav_genom_df.to_csv(BEHAV_DIR / 'AuxiliaryFiles' / \
                  '{}_checked_files.csv'.format(
                      datetime.datetime.today().strftime('%Y%m%d')),
                      index=False)
        missing_files = behav_genom_df[behav_genom_df.all(axis=1)]
        missing_files.to_csv(BEHAV_DIR / 'AuxiliaryFiles' /\
                              '{}_missing_files.csv'.format(
                                  datetime.datetime.today().strftime('%Y%m%d')))
        
    else:
        # load behavgenom results
        behavgenom_df = pd.read_csv('/Volumes/behavgenom$/Ida/Data/Hydra/DiseaseScreen/AuxiliaryFiles/20200914_checked_files.csv',
                                    index_col=False)
        df = behavgenom_df.drop(columns = ['masked_vid',
                                            'missing_masked',
                                            'results',
                                            'missing_results'])
        
    #%% and do checks against external hard drive
    SAVE_HD = HD_DIR / 'AuxiliaryFiles'
    SAVE_HD.mkdir(exist_ok=True)
    
    hd_df = df.copy()
    hd_df['full_path'] = hd_df.full_path.apply(lambda x: str(x).replace(str(BEHAV_DIR),
                                                                        str(HD_DIR)))
    hd_df = check_masked_results(hd_df)
    hd_df.to_csv(SAVE_HD / '{}_checked_files.csv'.format(
                     datetime.datetime.today().strftime('%Y%m%d')),
                 index=False
                 )
    
    missing_files_hd = hd_df[hd_df.all(axis=1)]
    
    missing_files_hd.loc[:,'bluelight'] = missing_files_hd['masked_vid'].apply(lambda x: str(x).split('_')[-3])
    missing_files_hd = missing_files_hd[ missing_files_hd['bluelight'] == 'prestim']
    missing_files_hd.to_csv(HD_DIR / 'AuxiliaryFiles' /\
                         '{}_missing_files.csv'.format(
                             datetime.datetime.today().strftime('%Y%m%d')),
                         index=False
                         )
