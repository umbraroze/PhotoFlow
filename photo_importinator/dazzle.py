#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

# Standard library
import sys
# PyPI
from colorama import Fore, Back, Style, just_fix_windows_console
import emoji
import progressbar

def endazzle_terminal():
    """Initialise terminal window so that it can accept "fancy" output."""
    # Initialise Colorama
    just_fix_windows_console()
    # Make sure progressbar magic can happen
    progressbar.streams.wrap_stderr()

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

def move_msg(source:str,destination:str):
    print(f"{source} {ICON_TO}  {destination}")
def convert_msg(source:str,destination:str):
    print(f"[Convert] {source} {ICON_TO}  {destination}")

# \uFE0F will encourage emoji rendering
ICON_DONE = emoji.emojize(':check_mark_button:',variant='emoji_type')
ICON_TO = emoji.emojize(':right_arrow:',variant='emoji_type')
ICON_WARN = emoji.emojize(':warning:',variant='emoji_type')
ICON_SKIP = emoji.emojize(':cross_mark_button:',variant='emoji_type') 
ICON_CLOUD = emoji.emojize(':cloud:',variant='emoji_type')
