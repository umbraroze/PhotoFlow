############################################################
# PowerShell script for archiving photographs.
# Uses 7-Zip.
############################################################

param (
    # Card device
    [string]$card = "F:\",
    # Where will we store the output file?
    [string]$outputdir = "D:\",
    # What's the camera name?
    [string]$camera = "Unknown_Camera"
)

Write-Output @"
-------------------------------------------------------------------
Photo archival tool
Creating a dated 7zip archive of the photos on the SD card.
-------------------------------------------------------------------
Command line settings:
 -card `"${card}`"
 -outputdir `"${outputdir}`"
 -camera `"${camera}`"
-------------------------------------------------------------------
If information isn't correct, press Ctrl+C to abort.
"@
Pause

############################################################
# Add location of 7z.exe to the path
$env:Path += ";${env:ProgramFiles}\7-Zip";

# Figure out input and output destinations
Try
{
    $cardpath = Resolve-Path $card -ErrorAction Stop
}
Catch [System.Management.Automation.DriveNotFoundException]
{
    Write-Error "Source card ${card} doesn't seem to be inserted. Exiting."
    Break
}
$inputdir = Join-Path $cardpath "DCIM" -ErrorAction Stop
if (-Not (Test-Path $inputdir)) {
    Write-Error "Source card ${card} doesn't seem to have a DCIM folder. Exiting."
    Break
}
$datestamp = Get-Date -format "yyyyMMdd"
Try
{
    $archive = Join-Path (Resolve-Path $outputdir) "${camera}_${datestamp}.7z"
}
Catch
{
    Write-Error "Output directory ${outputdir} doesn't seem to exist. Exiting."
    Break
}

Write-Output @"
Input folder: ${inputdir}
Output archive: ${archive}
"@

& 7z.exe a -t7z -r $archive $inputdir 

