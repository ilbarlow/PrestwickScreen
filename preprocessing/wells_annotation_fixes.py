#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 10:56:15 2020

@author: ibarlow
"""

import h5py
from pathlib import Path

annotations_file = Path('/Volumes/Ashur Pro2/PrestwickScreen/AuxiliaryFiles/20201127/PrestwickScreen_20201211_102314_wells_annotations.hdf5')

if __name__ == "__main__":
    with h5py.File(annotations_file, 'r+') as fid:
        fid["/filenames_df"].attrs["working_dir"] = str('/Volumes/Ashur Pro2/PrestwickScreen/MaskedVideos/20201127')