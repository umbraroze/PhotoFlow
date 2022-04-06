<#
.SYNOPSIS
    A tool for moving photographs from SD cards and Dropbox to NAS.

.DESCRIPTION
    This tool will perform three steps of moving photographs from SD
    cards and dropbox to NAS.

    This program expects to find exiftool.exe on PATH, and expects
    7-Zip to be installed on default location.

    The configuration file (photo_importinator_config.json) should be
    put to $HOME\Documents\WindowsPowerShell\ folkder

.PARAMETER Card
    The SD card drive to import from (e.g. "D:\"). If specified as
    "Dropbox", will import from Dropbox Camera Uploads subfolder in
    current user's home folder instead.

.PARAMETER Camera
    Name of the camera to base the settings on.

.PARAMETER Backup
    The folder where backups should be stored. Can be set in the
    config file; if specified here, will override that value.

.PARAMETER Destination
    The destination folder for the images. Images will be temporarily
    put in subfolder "Incoming".

.PARAMETER Date
    Datestamp for the backup file name. Defaults to current day in
    YYYYMMDD format.

.PARAMETER SkipBackup
    Skip the backup step of the workflow - will not create an archive
    file of the photos on the card.

.PARAMETER SkipImport
    Skip the importing step of the workflow - will not move the photos
    to Incoming and will not move to subsequent folders.

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
    [string]$SettingsFile = (Join-Path `
        -Path ([Environment]::GetFolderPath('MyDocuments')+"\WindowsPowerShell\") `
        -ChildPath "photo_importinator_config.json")
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

############################################################
# MAIN PROGRAM

# The utilities we need. These can be overridden in the
# config file if needed.
$7zip = "${env:ProgramFiles}\7-Zip\7z.exe"
$exiftool = "exiftool.exe"

# Read the settings.
$settings = Get-Content -Path $SettingsFile -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop

if(-Not $settings.Cameras.$Camera) {
    throw "Can't find camera $Camera in settings"
}
if($settings.Tools.SevenZip) { $7zip = $settings.Tools.SevenZip }
if($settings.Tools.ExifTool) { $exiftool = $settings.Tools.ExifTool }
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
if($settings.Cameras.$Camera.Card) {
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
  Destination:   ${Destination}
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
    Write-Output (([char]0x26A0)+" Skipping backup")
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

    & $7zip a -t7z -r $archive $inputdir 
    if(!$?) {
        throw "7-Zip process returned an error"
    }
}

# Move the photos to the Incoming folder, and from there to the desired folder structure.
Write-Line
if($SkipImport) {
    Write-Output (([char]0x26A0)+" Skipping import")
} else {
    $t = Resolve-Path (Join-Path -Path $Destination -ChildPath "Incoming") -ErrorAction Stop
    # Move stuff from the card to Incoming
    if($Card -eq "Dropbox") {
        Write-Output "Dropbox folder ${inputdir}"
        Get-ChildItem $inputdir | ForEach-Object {
            $s = Join-Path -Path $inputdir -ChildPath $_ 
            Write-Output ("${s} "+[char]0x2b62+" ${t}")
            Move-Item $s $t
        }
    } else {
        Get-ChildItem $inputdir | ForEach-Object {
            $sf = Join-Path -Path $inputdir -ChildPath $_
            Write-Output "SD card DCIM subfolder ${sf}"
            Get-ChildItem $sf | ForEach-Object {
                $s = Join-Path -Path $sf -ChildPath $_ 
                Write-Output ("${s} "+[char]0x2b62+" ${t}")
                Move-Item $s $t
            }
        }
    }

    # Run ExifTool to import
    Write-Output "Moving the photos from Incoming to the destination folders..."
    $l = Get-Location
    Set-Location -Path $Destination
    # TODO: make the output folder format configurable???
    & $exiftool -r "-Directory<DateTimeOriginal" -d "%Y/%m/%d" Incoming
    $r = $?
    Set-Location $l
    if(!$r) {
        throw "ExifTool returned an error"
    }
}
