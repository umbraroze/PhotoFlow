#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025,2026 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import sys
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import progressbar

console = Console()

def endazzle_terminal():
    """Initialise terminal window so that it can accept "fancy" output."""
    # Make sure progressbar magic can happen
    progressbar.streams.wrap_stderr()

def print_separator_line():
    console.rule('',style='cyan')

def print_boxed_text(message:str):
    """Prints text inside a box."""
    print(Panel(Text.styled(message,style='bright_red',justify='center'),border_style='cyan'))

def skip_warn(message:str):
    """Prints a skip warning message.
    It is preceded by a skip icon emoji and displayed in bold."""
    print(f":cross_mark_button: [bright_white]{message}[/bright_white]")
def warn(message:str):
    """Prints a warning message.
    It is preceded by an warning emoji and displayed in yellow."""
    print(f":warning: [yellow]{message}[/yellow]")
def die(message:str,errcode:int=1):
    """Prints an error message and exits with specified error code.
    The message is preceded by an warning emoji and displayed
    in bright red."""
    print(f":warning: [bright_red]{message}[/bright_red]")
    sys.exit(errcode)

def move_msg(source:str,destination:str):
    print(f"{source} :right_arrow: {destination}")
def convert_msg(source:str,destination:str):
    print(f"[Convert] {source} :right_arrow: {destination}")
