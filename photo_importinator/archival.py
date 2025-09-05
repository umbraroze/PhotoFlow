#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

# standard library
from pathlib import Path
import logging
# PyPI
import py7zr

logger = logging.getLogger(__name__)

def archive(source:Path, target:Path):
    """Archive all files under `source` to 7-Zip file `target`.

    TODO: instead of using writeall() (which just silently hangs for
    a long time), this should
        - form a list of files under source folder and their sizes
        - use write() to save individual files
        - display a progress bar, updating it after each file written,
          reflecting file sizes
        - report file count, total uncompressed size, size of final
          archive and compression ratio
    
    This should probably be a bit more elegant. Yet, since this
    part of the process can't really be parallelised, expressing these
    as photo_processing.Task isn't really feasible. So this is
    really just a helper function at this point.
    """
    with py7zr.SevenZipFile(target, 'w') as archive:
        archive.writeall(source)
