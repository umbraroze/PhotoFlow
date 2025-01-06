#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import sys
from colorama import Fore, Back, Style

def print_separator_line():
    print(Fore.CYAN + "\u2500"*70 + Style.RESET_ALL)

def print_boxed_text(str:str):
    """Prints text inside a box."""
    if len(str) > 68:
        raise RuntimeError
    if len(str) % 2 != 0:
        str = str + " "
    spaces = int((68.0/2.0) - (float(len(str))/2.0))
    print(Fore.CYAN+"\u250c"+("\u2500"*68)+"\u2510")
    print(Fore.CYAN+"\u2502"+Fore.RED+Style.BRIGHT+(" "*spaces)+str+(" "*spaces)+Style.RESET_ALL+Fore.CYAN+"\u2502")
    print(Fore.CYAN+"\u2515"+("\u2500"*68)+"\u2518"+Style.RESET_ALL)

def skip_warn(str:str):
    """Prints a skip warning message.
    It is preceded by a skip icon emoji and displayed in bold."""
    print(f"{Style.BRIGHT}{ICON_SKIP}  {str}{Style.RESET_ALL}")
def warn(str:str):
    """Prints a warning message.
    It is preceded by an warning emoji and displayed in yellow."""
    print(f"{Fore.YELLOW}{ICON_WARN}  {str}{Style.RESET_ALL}")
def die(str:str,errcode:int=1):
    """Prints an error message and exits with specified error code.
    The message is preceded by an warning emoji and displayed
    in bright red."""
    print(f"{Fore.RED}{Style.BRIGHT}{ICON_WARN}  {str}{Style.RESET_ALL}")
    sys.exit(errcode)

# \uFE0F will encourage emoji rendering
ICON_TO = "\u27A1\uFE0F"
ICON_WARN = "\u26A0\uFE0F" 
ICON_SKIP = "\u274E\uFE0F"
ICON_CLOUD = "\u2601\uFE0F"
