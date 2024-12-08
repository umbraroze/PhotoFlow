
from colorama import Fore, Back, Style

# function Write-Line {
#     Write-Host -ForegroundColor Cyan ([string]([char]0x2500) * 70)
# }

def print_separator_line():
    print(Fore.CYAN + "\u2500"*70 + Style.RESET_ALL)

# function Write-Box {
#     Param([string]$Text)
#     if($Text.Length % 2 -ne 0) {
#         $Text = $Text + " "
#     }
#     $spaces = (68/2) - ($Text.Length / 2)
##     Write-Host -ForegroundColor Cyan -NoNewline ([char]0x250c)
##     Write-Host -ForegroundColor Cyan -NoNewline ([string]([char]0x2500) * 68)
##     Write-Host -ForegroundColor Cyan ([char]0x2510)
##     Write-Host -ForegroundColor Cyan -NoNewline ([char]0x2502)
##     Write-Host -ForegroundColor Red -NoNewline (" " * $spaces)
##     Write-Host -ForegroundColor Red -NoNewline $Text
##     Write-Host -ForegroundColor Red -NoNewline (" " * $spaces)
##     Write-Host -ForegroundColor Cyan ([char]0x2502)
##     Write-Host -ForegroundColor Cyan -NoNewline ([char]0x2514)
##     Write-Host -ForegroundColor Cyan -NoNewline ([string]([char]0x2500) * 68)
##     Write-Host -ForegroundColor Cyan ([char]0x2518)
# }

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
