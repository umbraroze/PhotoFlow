#!/usr/bin/python

from sidecar_data import get_sidecar
from pathlib import Path
import os

file = Path.home() / 'Desktop/NC_FLLST.DAT'

sidecar = get_sidecar(file)

for e in sorted(sidecar.keys()):
    if 'rating' in sidecar[e] and sidecar[e]['rating'] != 'TRASH':
        r = '*' * sidecar[e]['rating']
        print(f"{e} - {r}")
