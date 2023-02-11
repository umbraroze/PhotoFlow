# Renames video files from HDV_0001.MP4 to yyyymmdd_hhmmss_HDV_0001.mp4

#$infiles = @(Get-Item *.MP4) + @(Get-Item *.MOV);
$infiles = Get-Item *.MP4
$infiles | ForEach-Object {
    $in = $_;
    $d = Get-Date -UFormat "%Y%m%d_%H%M%S" $in.LastWriteTime;
    $p = Split-Path $in;
    $out = $p  + "\" + $d + "_" + $in.BaseName + ".mp4";
    Write-Output "`n`nProcessing $in => $out`n`n";
    Move-Item $in $out
}
# FIXME: STUPID COPYPASTE HACK
$infiles = Get-Item *.MOV
$infiles | ForEach-Object {
    $in = $_;
    $d = Get-Date -UFormat "%Y%m%d_%H%M%S" $in.LastWriteTime;
    $p = Split-Path $in;
    $out = $p  + "\" + $d + "_" + $in.BaseName + ".mov";
    Write-Output "`n`nProcessing $in => $out`n`n";
    Move-Item $in $out
}
$infiles = Get-Item *.avi
$infiles | ForEach-Object {
    $in = $_;
    $d = Get-Date -UFormat "%Y%m%d_%H%M%S" $in.LastWriteTime;
    $p = Split-Path $in;
    $out = $p  + "\" + $d + "_" + $in.BaseName + ".avi";
    Write-Output "`n`nProcessing $in => $out`n`n";
    Move-Item $in $out
}
