# Moves files into day-based subfolders based on modification timestamp.

$infiles = Get-Item *
$infiles | ForEach-Object {
    $in = $_;
    $d = Get-Date -UFormat "%Y-%m-%d" $in.LastWriteTime;
    $p = Split-Path $in;

    if(-Not (Test-Path $d)) {
        $null = New-Item -Name $d -ItemType "directory"
    }

    $out = $p  + "\" + $d + "\" + $in.Name;
    Write-Output "`n`nProcessing $in => $out`n`n";
    Move-Item $in $out
}