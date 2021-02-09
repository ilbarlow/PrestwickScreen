#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:23:44 2021

@author: ibarlow

Script to check prestwick data for visible phenotypes in control drugs:
    Olanzapine
    Chlorpromazine
    Raclopride
    Haloperidol
    CSAA466656
    
Export the wells of these drugs (and some controls to a .csv to then visually 
check in tierpsy viewer
"""

import pandas as pd
from pathlib import Path

METADATA_FNAME = Path('/Volumes/behavgenom$/Ida/Data/Hydra/PrestwickScreen/AuxiliaryFiles/wells_updated_metadata.csv')

CONTROL = 'DMSO'
CONTROL_DRUGS = ['Olanzapine',
                'Chlorpromazine',
                'Raclopride',
                'Haloperidol',
                'CSAA466656']

if __name__ == '__main__':
    meta = pd.read_csv(METADATA_FNAME)
    
    to_export = meta.query('@CONTROL_DRUGS in drug_type or @CONTROL in drug_type')
    
    prestim_only = [i for i,r in to_export.iterrows() if 'prestim' in r.imgstore_name]
    
    to_export = to_export.loc[prestim_only,:]

    # to_export[['drug_type',
    #            'imaging_plate_drug_concentration',
    #            'well_name',
    #            'imgstore_name',
    #            'date_yyyymmdd', ]].to_csv(METADATA_FNAME.parent / 'control_drugs_visual_checks.csv',
    #                                       index=False)
                                          
    # meta.query('20201127 in date_yyyymmdd')

    # meta_checks = meta.drop_duplicates(subset=['imaging_plate_id',
    #                                            'imgstore_name'])
    meta_checks = meta[meta.well_name == 'A1']
    meta_checks = meta_checks[meta_checks.imgstore_name.notna()]
    meta_checks = meta_checks.loc[[i for i,r in meta_checks.iterrows() if 'prestim' in r.imgstore_name],:]
    
    meta_checks.sort_values(by=['date_yyyymmdd',  'imaging_run', 'instrument_name'], inplace=True)
    meta_checks['imgstore_name'] = meta_checks.loc[:, 'imgstore_name'].apply(lambda x: x.split('.')[0])
    meta_checks['imgstore_name'] = meta_checks.loc[:, 'imgstore_name'].apply(lambda x: x.split('/')[1])

    meta_checks[['imaging_plate_id',
                 'date_yyyymmdd',
                 'imaging_run_number',
                 'instrument_name',
                 'imgstore_name']].to_csv(METADATA_FNAME.parent / 'check_sensors_data.csv',
                                          index=False)