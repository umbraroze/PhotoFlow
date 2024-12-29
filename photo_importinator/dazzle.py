#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

from colorama import Fore, Back, Style

def print_separator_line():
    print(Fore.CYAN + "\u2500"*70 + Style.RESET_ALL)

def print_boxed_text(str):
    """Prints text inside a box."""
    if len(str) > 68:
        raise RuntimeError
    if len(str) % 2 != 0:
        str = str + " "
    spaces = int((68.0/2.0) - (float(len(str))/2.0))
    print(Fore.CYAN+"\u250c"+("\u2500"*68)+"\u2510")
    print(Fore.CYAN+"\u2502"+Fore.RED+(" "*spaces)+str+(" "*spaces)+Fore.CYAN+"\u2502")
    print(Fore.CYAN+"\u2515"+("\u2500"*68)+"\u2518"+Style.RESET_ALL)

# \uFE0F will encourage emoji rendering
ICON_TO = "\u27A1\uFE0F"
ICON_WARN = "\u26A0\uFE0F" 
ICON_SKIP = "\u274E\uFE0F"
ICON_CLOUD = "\u2601\uFE0F"
