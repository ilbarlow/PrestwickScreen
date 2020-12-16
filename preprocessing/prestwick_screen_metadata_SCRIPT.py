#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 10:14:09 2020

@author: ibarlow

script for generating the metadata from the prestwick screen

Parent directory (Auxiliary Files) contains individual folders for each
day of experiments, and contains the following files:
    YYYYMMDD_manual_metadata.csv (DD = day of tracking (d))
    YYYYMMDD_wormsorter.csv (DD = day of tracking)
    YYYMMDD_robot_bad_imaging_wells.csv (DD = day of tracking)
    
There is one sourceplates file that was generated prior to all imaging
runs using the opentrons robot:
    /PrestwickScreen/AuxiliaryFiles/sourceplates/prestwick_sourceplates_shuffled_FINAL.csv


The following files will be generated: 
    YYYYMMDD_plate_metadata.csv:
        this is generated from the wormsorter files
    YYYYMMDD_day_metadata.csv:
        compiled metadata from all the UI .csv files
    
    metadata.csv - final concatenated metadata of all the days combined

"""

import pandas as pd
from pathlib import Path
from tierpsytools.hydra.compile_metadata import populate_96WPs,\
    convert_bad_wells_lut, get_day_metadata, day_metadata_check,\
    concatenate_days_metadata, number_wells_per_plate
import re

date_regex = r"\d{8}"
plate_id_regex= r""
ROOT_DIR = Path('/Volumes/behavgenom$/Ida/Data/Hydra/PrestwickScreen')
AUX_DIR = ROOT_DIR / 'AuxiliaryFiles'

# import the shuffled plates as a reference
SOURCEPLATES = list(AUX_DIR.rglob('*sourceplates_shuffled_FINAL.csv'))[0]

drug_plates = pd.read_csv(SOURCEPLATES)

# %% 
if __name__=='__main__':
    day_root_dirs = [d for d in AUX_DIR.glob("*")
                     if d.is_dir() and re.search(date_regex, str(d))
                     is not None]
    
    print('Calculating metadata for {} days of experiments'.format(
            len(day_root_dirs)))
    
    for count, day in enumerate(day_root_dirs):
        exp_date = re.findall(date_regex, str(day))[0]
        manualmetadata_file = list(day.rglob('*_manual_metadata.csv'))[0]
        assert (exp_date in str(manualmetadata_file))
        wormsorter_file = list(day.rglob('*_wormsorter.csv'))[0]
        assert (exp_date in str(wormsorter_file))
        bad_wells_file = list(day.rglob('*_robot_bad_imaging_wells.csv'))[0]
        assert (exp_date in str(bad_wells_file))
        
        print('Collating wormsorter files: {}'.format(wormsorter_file))
        
        plate_metadata = populate_96WPs(wormsorter_file,
                                        del_if_exists=True,
                                        saveto='default')
        
        bad_wells_df = convert_bad_wells_lut(bad_wells_file)
        
        plate_metadata = pd.merge(plate_metadata,
                                  bad_wells_df,
                                  on=['imaging_plate_id', 'well_name'],
                                  how='outer')
        plate_metadata['is_bad_well'].fillna(False,
                                             inplace=True)
        metadata_file = day / '{}_day_metadata.csv'.format(exp_date)
    
        print('Generating day metadata: {}'.format(
                metadata_file))
        
        try:
            day_metadata = get_day_metadata(plate_metadata,
                                            manualmetadata_file,
                                            saveto=metadata_file,
                                            del_if_exists=True,
                                            include_imgstore_name=True)
        except ValueError:
            print('imgstore error')
            day_metadata = get_day_metadata(plate_metadata,
                                            manualmetadata_file,
                                            saveto=metadata_file,
                                            del_if_exists=True,
                                            include_imgstore_name=False)
        
        day_metadata['source_plate_id'] = day_metadata['imaging_plate_id'
                                                       ].apply(lambda x: '_'.join(x.split('_')[:-1]))
        day_metadata = pd.merge(day_metadata,
                               drug_plates,
                               left_on=['source_plate_id',
                                        'well_name'],
                               right_on=['shuffled_plate_id',
                                         'destination_well'],
                               suffixes=('_day', '_robot'),
                               how='outer')
        day_metadata.drop(
            day_metadata[day_metadata['imaging_plate_id'].isna()].index,
                        inplace=True)
           
        files_to_check = day_metadata_check(day_metadata, day, plate_size=48)
        number_wells_per_plate(day_metadata, day)
        
        day_metadata.to_csv(metadata_file, index=False)
    
    # %%concatenate day metadata
    
    # combine all the metadata files
    compiled_meta = concatenate_days_metadata(AUX_DIR,
                                              list_days=None,
                                              saveto=None)
    
