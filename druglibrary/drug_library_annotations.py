#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 14:45:35 2021

@author: ibarlow

Group the drugs columns in the prestwick library groups:
    Therapeutic group
    Principal target
    Side Effects
    
    - check these for any typos and spelling errors and update in the library files
    - export .csv with the drugs and all their moas 
    
    

"""
from pathlib import Path
import pandas as pd
import numpy as np


LIBRARY = Path('/Users/ibarlow/OneDrive - Imperial College London/Documents/DrugScreening/DrugLibraries/Prestwick_CelegansLibrary/Prestwick_Celegans_Library_IBedits.xlsx')

GROUPINGS = ['Therapeutic group',
             'Principal target',
             'Side Effects']

if __name__ == '__main__':
    prestwick_df = pd.read_excel(LIBRARY)
    
    len(prestwick_df.groupby('Therapeutic group').groups)
    
    len(prestwick_df.groupby('Principal target').groups)
    
    len(prestwick_df.groupby('Side Effects').groups)
    
    
    prestwick_df.groupby('Therapeutic group')['chemical name'].size().to_csv(LIBRARY.parent / 'Therapeutic_groups.csv')   
    prestwick_df.groupby('Principal target')['chemical name'].size().to_csv(LIBRARY.parent / 'Principal_targets.csv')  
    prestwick_df.groupby('Side Effects')['chemical name'].size().to_csv(LIBRARY.parent / 'Side_Effects.csv')
    
    
    prestwick_annotations = []
    for c, g in enumerate(GROUPINGS):
        prestwick_annotations.append(prestwick_df.groupby('chemical name').apply(lambda x: '; '.join([str(y) for y in x[g] if y is not np.nan])).to_frame())
    
    prestwick_annotations = pd.concat(prestwick_annotations, axis=1)
    prestwick_annotations.columns = GROUPINGS
    
    prestwick_annotations = pd.merge(prestwick_annotations,
                                     prestwick_df,
                                     how='outer',
                                     on='chemical name')
    
    prestwick_annotations.drop_duplicates(subset='chemical name',
                                         inplace=True)
    prestwick_annotations.drop(columns=['{}_y'.format(g) for g in GROUPINGS],
                               inplace=True)
    prestwick_annotations.drop(columns=['structure',
                                       'Drug Concentration'],
                               inplace=True)
    prestwick_annotations.rename(columns={k:k.split('_')[0] for k in prestwick_annotations.columns},
                                 inplace=True)
    
    prestwick_annotations.to_csv(LIBRARY.parent / 'Celegans_prestwick_annotations.csv',
                                 index=False)
    
    
    
