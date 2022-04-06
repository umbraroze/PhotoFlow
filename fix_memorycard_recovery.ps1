# Postprocessing stuff from Recuva SD card recovery. Results in files
# like "[000001].tif", with DNG files identified as TIFFs. Rename all
# files to img000001.dng or .jpg as appropriate. Fix file timestamps
# using exiftool.
foreach ($item in (Get-Item *.tif)) {
    $oldname = ($item.Name)
    if($oldname -match '[\[\]]') {
        $newname = ("img" + $item.Basename + ".dng") -Replace '[\[\]]',''
        Move-Item -LiteralPath $oldname -Destination $newname
        Write-Output "${oldname} -> ${newname}"
    } else {
        Write-Output "${oldname} OK"
    }
}
foreach ($item in (Get-Item *.jpg)) {
    $oldname = ($item.Name)
    if($oldname -match '[\[\]]') {
        $newname = ("img" + $item.Name) -Replace '[\[\]]',''
        Move-Item -LiteralPath $oldname -Destination $newname
        Write-Output "${oldname} -> ${newname}"
    } else {
        Write-Output "${oldname} OK"
    }
}
Write-Output "Renaming done, fixing dates..."
& exiftool.exe '-FileModifyDate<DateTimeOriginal' *.dng *.jpg
