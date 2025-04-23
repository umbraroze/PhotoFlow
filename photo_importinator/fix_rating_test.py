#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import os, sys
import subprocess
from pathlib import Path
import exiv2

def fix_dng_rating_from_raw(source_raw:Path, target_dng:Path):
    try:
        source_img = exiv2.ImageFactory.open(str(source_raw))
        target_img = exiv2.ImageFactory.open(str(target_dng))
    except exiv2.Exiv2Error:
        sys.exit(1)
    source_img.readMetadata()
    target_img.readMetadata()
    source_img_data = source_img.xmpData()
    target_img_data = target_img.xmpData()
    try:
        rating = source_img_data["Xmp.xmp.Rating"].getValue()
    except exiv2.Exiv2Error:
        rating = 0
    if rating != 0:
        target_img_data["Xmp.xmp.Rating"] = rating
        target_img.writeMetadata()
    print(f"Rating: {rating}")

if __name__ == '__main__':
    source_file = Path.home() / 'Desktop/Temporary/DSC_5773.NEF'
    target_file = Path.home() / 'Desktop/Temporary/DSC_5773.DNG'

    if os.path.exists(target_file):
        os.unlink(target_file)
    cmd = [Path('C:/PortApps/dnglab-bin/dnglab.exe'),'convert',source_file,target_file]
    result = subprocess.run(cmd,capture_output=True,check=True)
    fix_dng_rating_from_raw(source_file,target_file)

