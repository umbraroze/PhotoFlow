#!/usr/bin/python
#
# Photo Importinator III: This Time It's Python For Some Reason
#

# Built-in modules
import os, sys
import re

# https://pypi.org/project/colorama/
import colorama

from configuration import CLIOptions

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""
    
    # Initialise Colorama
    colorama.just_fix_windows_console()
    
    # Parse arguments
    opts = CLIOptions.getopt()
    #print(opts)

    return 0

if __name__ == '__main__':
    main()
