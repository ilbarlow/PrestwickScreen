#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 08:42:40 2020

@author: ibarlow

Script to fill the 96WPs with 3 doses of each drug from the Prestwick C elegans
library that contains 240 drugs

"""

import pandas as pd
from pathlib import Path
import numpy as np
import itertools
import math
import warnings

PRESTWICK_LIBRARY = Path('/Users/ibarlow/OneDrive - Imperial College London/'+\
                         'Documents/DrugScreening/DrugLibraries/' +\
                             'Prestwick_CelegansLibrary/'+\
                                 'Celegans_Library_240_IBedits.csv')

SAVE_TO = PRESTWICK_LIBRARY.parent / '2020PrestwickLibraryPlates3doses.csv'
    
CONTROL_DICT = {'DMSO': 5,
                'NoCompound': 4}
NO_CONTROLS = CONTROL_DICT['DMSO'] + CONTROL_DICT['NoCompound']

MIN_VOLUME_REQUIRED_ul = 20
STOCK_CONCENTRATIONS_M = [0.1, 0.01, 0.001]
MAX_NUMBER_CONCENTRATIONS = 3

# 96well plate format
COLUMNS96WP = np.arange(1, 13)
ROWS96WP = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
WELLS96WP =  [''.join([i[0], str(i[1]).zfill(2)]) for i in
             list(itertools.product(ROWS96WP, COLUMNS96WP))]

CONTROL_WELLS = WELLS96WP[-NO_CONTROLS:]




if __name__ == '__main__':
    prestwick_drugs = pd.read_csv(PRESTWICK_LIBRARY)
    
    prestwick_drugs['number_concentrations'] = MAX_NUMBER_CONCENTRATIONS
    prestwick_drugs['maximum_concentration_M'] = STOCK_CONCENTRATIONS_M[0]
    prestwick_drugs['number_replicates'] = 4
    
    prestwick_drugs['vol_DMSO_to_add_for_max_concentration_ul'] =[
        ((r.mass_supplied_g/r.mol_weight_structure)*1000/r.maximum_concentration_M)*1000
        for i,r in prestwick_drugs.iterrows()]
    

#%%
    number_conditions = sum(prestwick_drugs['number_concentrations'])
    number_plates = math.ceil(number_conditions /
                              (len(WELLS96WP) - NO_CONTROLS))

    libraryDF = pd.DataFrame(columns=['drug_type',
                                      'drug_code',
                                      'drug_concentration'
                                      ])
    libraryDF['library_plate_number'] = sum([len(WELLS96WP)*[p] for p in
                                             range(1, number_plates+1)], [])
    libraryDF['well_name'] = WELLS96WP * number_plates

    # loop through the drugs and assign to the wells
    well_counter = 0
    for i, r in prestwick_drugs.iterrows():
        if libraryDF.loc[well_counter].well_name >= CONTROL_WELLS[0]:
            libraryDF.loc[well_counter:well_counter + CONTROL_DICT['DMSO']-1,
                          ['drug_type',
                           'drug_code',
                           'drug_concentration']] = 'DMSO', 'DMSO', 0.001
            well_counter += CONTROL_DICT['DMSO']
            libraryDF.loc[well_counter:well_counter + CONTROL_DICT['NoCompound']-1,
                          ['drug_type',
                           'drug_code',
                           'drug_concentration']] = 'NoCompound', 'NoCompound', 0

            well_counter += CONTROL_DICT['NoCompound']

            libraryDF.loc[well_counter:well_counter+r.number_concentrations-1,
                          ['drug_type',
                           'drug_code',
                           'drug_concentration']] = r.chemical_name,r.Compound_Identifying_Number, STOCK_CONCENTRATIONS_M
    
            well_counter += r.number_concentrations

        else:
            libraryDF.loc[well_counter:well_counter+r.number_concentrations-1,
                          ['drug_type',
                           'drug_code',
                           'drug_concentration']] = r.chemical_name, r.Compound_Identifying_Number, STOCK_CONCENTRATIONS_M
            well_counter += r.number_concentrations


    library_export = libraryDF.merge(prestwick_drugs[['Compound_Identifying_Number',
                                                      'chemical_name',
                                                      'mol_weight_structure',
                                                      'mass_supplied_g',
                                                      'maximum_concentration_M',
                                                      'vol_DMSO_to_add_for_max_concentration_ul'
                                                      ]],
                                     left_on='drug_code',
                                     right_on='Compound_Identifying_Number',
                                     how='outer')
    
    library_export.drop(columns=['Compound_Identifying_Number',
                                 'chemical_name'],
                        inplace=True)
    library_export.sort_values(by=['library_plate_number',
                                   'well_name'],
                               inplace=True)
    
    if SAVE_TO.exists():
        warnings.warn('Sygenta 3 dose .csv file already exists')
    else:
        library_export.to_csv(SAVE_TO, index=False)
