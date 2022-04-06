############################################################
# PowerShell script for archiving photographs from Dropbox.
# Uses 7-Zip.
############################################################

param (
    # Where will we store the output file?
    [string]$outputdir = "D:\",
    # What's the camera name?
    [string]$camera = "Unknown_Camera"
)

Try
{
    $inputdir = Resolve-Path "${HOME}\Dropbox\Camera Uploads" -ErrorAction Stop
}
Catch
{
    Write-Error "Can't find Dropbox Camera Uploads folder"
    Break
}

Write-Output @"
-------------------------------------------------------------------
Dropbox photo archival tool
Creating a dated 7zip archive of the photos on Dropbox Camera Uploads.
-------------------------------------------------------------------
Source folder: ${inputdir}
Command line settings:
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

& 7z.exe a -t7z -x'!*.ini' -r $archive $inputdir 




