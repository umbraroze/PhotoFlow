<#
.SYNOPSIS
    A tool for moving photographs from SD cards and Dropbox to NAS.

.DESCRIPTION
    This tool will perform three steps of moving photographs from SD
    cards and dropbox to NAS.

    This program expects to find exiv2 on PATH, and expects
    7-Zip to be installed on default location. Exact paths of
    these utilities can be overridden in the configuration file.

.PARAMETER Card
    The SD card drive to import from (e.g. "D:"). If specified as
    "Dropbox", will import from Dropbox "Camera Uploads" subfolder in
    current user's home folder instead.

.PARAMETER Camera
    Name of the camera to base the settings on.

.PARAMETER Backup
    The folder where backups should be stored. Can be set in the
    config file; if specified here, will override that value.

.PARAMETER Destination
    The base destination folder for the images.

.PARAMETER FolderStructure
    The folder structure for images, using the original photo date.
    Default: '{0:yyyy}/{0:MM}/{0:dd}'

.PARAMETER Date
    Datestamp for the backup file name. Defaults to current day in
    yyyyMMdd format.

.PARAMETER SkipBackup
    Skip the backup step of the workflow - will not create an archive
    file of the photos on the card.

.PARAMETER SkipImport
    Skip the importing step of the workflow - will not move the photos
    to Incoming and will not move to subsequent folders.

.PARAMETER DryRun
    Do all the actions except actually moving/backing up the files.
    Will print out what actions would be performed instead.

.PARAMETER SettingsFile
    Where script settings are located. Default
    "~\Documents\WindowsPowerShell\photo_importinator_config.psd1".

.NOTES
    Filename: photo_importinator.ps1
    Author: Rose Midford
#>

############################################################
# SCRIPT PARAMETERS
############################################################
Param(
    [Parameter(Mandatory=$true)][string]$Camera,
    [string]$Card,
    [string]$Backup,
    [string]$Destination,
    [string]$Date = (Get-Date -Format "yyyyMMdd"),
    [switch]$SkipBackup,
    [switch]$SkipImport,
    [switch]$DryRun,
    [string]$SettingsFile = (Join-Path `
        -Path ([Environment]::GetFolderPath('MyDocuments')+"\WindowsPowerShell\") `
        -ChildPath "photo_importinator_config.psd1")
)

############################################################
# FUNCTIONS
############################################################

function Write-Line {
    Write-Host -ForegroundColor Cyan ([string]([char]0x2500) * 70)
}
function Write-Box {
    Param([string]$Text)
    if($Text.Length % 2 -ne 0) {
        $Text = $Text + " "
    }
    $spaces = (68/2) - ($Text.Length / 2)
    Write-Host -ForegroundColor Cyan -NoNewline ([char]0x250c)
    Write-Host -ForegroundColor Cyan -NoNewline ([string]([char]0x2500) * 68)
    Write-Host -ForegroundColor Cyan ([char]0x2510)
    Write-Host -ForegroundColor Cyan -NoNewline ([char]0x2502)
    Write-Host -ForegroundColor Red -NoNewline (" " * $spaces)
    Write-Host -ForegroundColor Red -NoNewline $Text
    Write-Host -ForegroundColor Red -NoNewline (" " * $spaces)
    Write-Host -ForegroundColor Cyan ([char]0x2502)
    Write-Host -ForegroundColor Cyan -NoNewline ([char]0x2514)
    Write-Host -ForegroundColor Cyan -NoNewline ([string]([char]0x2500) * 68)
    Write-Host -ForegroundColor Cyan ([char]0x2518)
}

function Move-ImageFolder {
    Param([string]$InFolder,[string]$OutFolder,[string[]]$Ignored)
    $items = Get-ChildItem $InFolder
    :image foreach($_ in $items) {
        # Get the full source image path 
        $Source = Join-Path -Path $InFolder -ChildPath $_ 
        # Check of the file is ignored
        if($Ignored) {
            foreach($i in $Ignored) {
                if([io.path]::GetFileName($Source) -eq $i) {
                    Write-Output "${Source} ignored"
                    continue image
                }
            }
        }
        # Get the datestamp and format it into a folder name (or "Incoming" if unknown)
        if(-Not ((& $Exiv2 --key 'Exif.Photo.DateTimeOriginal' $Source) -match '(\d\d\d\d:\d\d:\d\d \d\d:\d\d:\d\d)$')) {
            Write-Host -ForegroundColor Yellow (([char]0x26A0)+" No original date for $Source, putting it to Incoming")
            $DateFolder = "Incoming"
        } else {
            $DateFolder = $FolderStructure -f [DateTime]::parseexact($Matches[1],'yyyy:MM:dd HH:mm:ss',$null)    
        }
        # Form the full target folder and file paths
        $TargetFolder = Join-Path -Path $OutFolder -ChildPath $DateFolder
        $Target = Join-Path -Path $TargetFolder -ChildPath $_
        # Strip the "Microsoft.PowerShell.Core\FileSystem::" part from target
        # for display purposes.
        # FIXME: This should actually use something like Convert-Path, but
        # Convert-Path requires path to be resolvable.
        $DispTarget = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Target)
        # Create the target folder if it doesn't exist
        if(-Not (Test-Path $TargetFolder)) {
            if($DryRun) {
                Write-Host -ForegroundColor Yellow (([char]0x26A0)+" Would create a folder")
            } else {
                $null = New-Item $TargetFolder -ItemType Directory
            }
        }
        # Perform the actual move.
        if($DryRun) {
            Write-Output ("Would move: ${Source} "+[char]0x27a1+" ${DispTarget}")
        } else {            
            Write-Output ("${Source} "+[char]0x27a1+" ${DispTarget}")
            Move-Item $Source $Target
        }
    }
}


############################################################
# MAIN PROGRAM

# The utilities we need. These can be overridden in the
# config file if needed.
$7zip = "${env:ProgramFiles}\7-Zip\7z.exe" # Default install location
$exiv2 = "exiv2.exe" # Assumed to be on path somewhere

# Read the settings.
$settings = Import-PowerShellDataFile $SettingsFile -ErrorAction Stop

if(-Not $settings.Cameras.$Camera) {
    throw "Can't find camera $Camera in settings"
}
if($settings.Tools.SevenZip) { $7zip = $settings.Tools.SevenZip }
if($settings.Tools.Exiv2) { $exiv2 = $settings.Tools.Exiv2 }
if(-Not $Backup) {
    if($settings.Cameras.$Camera.Backup) {
        $Backup = $settings.Cameras.$Camera.Backup
    } else {
        $Backup = $settings.Backup
    }
}
if(-Not $Destination) {
    if($settings.Cameras.$Camera.Destination) {
        $Destination = $settings.Cameras.$Camera.Destination
    } else {
        $Destination = $settings.Destination
    }
}
if(-Not $FolderStructure) {
    if($settings.FolderStructure) {
        $FolderStructure = $settings.FolderStructure
    } else {
        $FolderStructure = '{0:yyyy}/{0:MM}/{0:dd}'
    }
}
$ExampleDestination = Join-Path -Path $Destination -ChildPath ($FolderStructure -replace '\{0:(.*?)\}','$1')
if((-Not $Card) -and $settings.Cameras.$Camera.Card) {
    $Card = $settings.Cameras.$Camera.Card
}

# Print out the banner and the final configuration details.
Write-Box "PHOTO IMPORTINATOR"
Write-Line
Write-Output @"
Settings file:   ${SettingsFile}
Settings:
  Camera:        ${Camera}
  Card:          ${Card}
  Backup folder: ${Backup}
  Destination:   ${ExampleDestination}
"@
Write-Line

if (-Not $Card) {
    throw "Card is unspecified"
}
if (-Not $Backup) {
    throw "Backup folder is unspecified"
}
if (-Not $Destination) {
    throw "Destination folder is unspecified"
}

Write-Output "If information isn't correct, press Ctrl+C to abort."
Pause

############################################################

# Figure out input and output destinations
if($Card -eq "Dropbox") {
    Try
    {
        $inputdir = Resolve-Path "${HOME}\Dropbox\Camera Uploads" -ErrorAction Stop
    }
    Catch
    {
        throw "Can't find Dropbox Camera Uploads folder"
    }        
} else {
    Try
    {
        $cardpath = Resolve-Path $Card -ErrorAction Stop
    }
    Catch [System.Management.Automation.DriveNotFoundException]
    {
        throw "Source card ${Card} doesn't seem to be inserted. Exiting."
    }
    $inputdir = Join-Path $cardpath "DCIM" -ErrorAction Stop
    if (-Not (Test-Path $inputdir)) {
        throw "Source card ${Card} doesn't seem to have a DCIM folder. Exiting."
    }
}

# Backup the card contents
Write-Line
if($SkipBackup) {
    Write-Host -ForegroundColor Yellow (([char]0x26A0)+" [Skipped] Entire backup phase")
} else {
    Try
    {
        $archive = Join-Path (Resolve-Path $Backup) "${Camera}_${Date}.7z"
    }
    Catch
    {
        throw "Output directory ${Backup} doesn't seem to exist. Exiting."
    }
    
    Write-Output "Input folder: ${inputdir}"
    Write-Output "Output archive: ${archive}"

    if($DryRun) {
        Write-Host -ForegroundColor Yellow (([char]0x26A0)+" [Skipped] ${7zip} a -t7z -r ${archive} ${inputdir}")
    } else {
        & $7zip a -t7z -r $archive $inputdir 
        if(!$?) {
            throw "7-Zip process returned an error"
        }
    }
}

# Move the photos to the Incoming folder, and from there to the desired folder structure.
Write-Line
if($SkipImport) {
    Write-Host -ForegroundColor Yellow (([char]0x26A0)+" [Skipped] Entire import phase")
} else {
    # Move stuff from the card to Incoming
    # TODO: Maybe move some of this stuff into functions???
    if($Card -eq "Dropbox") {
        Write-Output "Dropbox folder ${inputdir}"
        Move-ImageFolder -InFolder $inputdir -OutFolder $Destination -Ignored $settings.Cameras.$Camera.Ignore
    } else {
        Get-ChildItem $inputdir | ForEach-Object {
            $sourcefolder = Join-Path -Path $inputdir -ChildPath $_
            Write-Output "SD card DCIM subfolder ${sourcefolder}"
            Move-ImageFolder -InFolder $sourcefolder -OutFolder $Destination -Ignored $settings.Cameras.$Camera.Ignore
        }
    }
}
