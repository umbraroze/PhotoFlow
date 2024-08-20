#!/usr/bin/python
#
# Photo Importinator III: This Time It's Python For Some Reason
#

# Built-in modules
import os, sys
import re
import datetime
# https://docs.python.org/3/library/tomllib.html
import tomllib
# https://docs.python.org/3/library/argparse.html
import argparse

# PyPi modules
import exiv2
# https://pypi.org/project/colorama/
import colorama

###### Configuration #####################################################
class CLIOptions:
    """Parses script command line arguments for Photo Importinator."""
    @staticmethod
    def getopt():
        parser = argparse.ArgumentParser(
            prog='photo_importinator',
            description='Move or convert photos from SD card or cloud to your photo server.')
        # Target and destination specifications
        parser.add_argument('-T','--target',default=None,help="Specify target device (default: as set in config)")
        parser.add_argument('-c','--card',help='Card path/device (default: as per camera settings in config)')
        parser.add_argument('--date',
                            type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
                            default=datetime.date.today(),
                            help="Archive date stamp, YYYY-mm-dd (default: current date)")
        # Skipping switches
        parser.add_argument('--skip-backup',action='store_true',help="Skip backup phase")
        parser.add_argument('--skip-import',action='store_true',help="Skip the final import phase")
        parser.add_argument('--dry-run',action='store_true',help="Just look at files, do not actually do anything")
        # Camera
        parser.add_argument('camera',default=None,nargs='?',help="Camera name.")
        args = parser.parse_args()

class Configuration:
    """Photo Importinator's configuration."""
    class Camera:
        """Configuration for camera specific details."""
        card = None
        card_label = None
        ignore = None
        convert_raw = None


###### Photo processing task #############################################

class TargetDirectory:
    """Target directory. Tracks the date stamp for stats purposes."""
    pass

class PhotoProcessTask:
    """Task representing image moving or conversion. Keeps track of the
    state of the process and stats."""
    pass

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""
    
    # Initialise Colorama
    colorama.just_fix_windows_console()
    
    # Parse arguments
    CLIOptions.getopt()

    return 0

if __name__ == '__main__':
    main()
