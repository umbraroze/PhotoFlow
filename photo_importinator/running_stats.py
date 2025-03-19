#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import pickle
import logging
from pathlib import Path
from datetime import date

from configuration import Configuration

logger = logging.getLogger(__name__)

class RunningStats:
    """Running stats collector. The running stats are pickled into a dict
    with date (datetime.date) as key and running count (int) as value.
    
    Note: This implementation is pretty naive and not thread-safe in the slightest.
    Use only one running stats collector."""

    stats: dict = None
    db_file: Path = None

    def __init__(self,config:Configuration):
        self.db_file = config.default_running_stats_path()
        self.load()

    def load(self):
        try:
            f = open(self.db_file,'rb')
            self.stats = pickle.load(f)
            f.close()
            logger.debug(f"Running stats loaded from {self.db_file}")
        except FileNotFoundError:
            self.stats = {}
            logger.debug(f"Running stats not found, will be stored in {self.db_file} when saved")

    def increment_day(self,day:date):
        """Increment the specified day in the running count by one."""
        if day in self.stats:
            self.stats[day] += 1
        else:
            self.stats[day] = 1

    def save(self):
        f = open(self.db_file,'wb')
        pickle.dump(self.stats,f)
        f.close()
        logger.info(f"Running counts saved to {self.db_file}")