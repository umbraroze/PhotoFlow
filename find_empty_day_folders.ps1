#
# This will find all empty day subfolders in a directory tree structure like
# YYYY/MM/DD.
#

Get-ChildItem -Directory | Select-String -Pattern '^\d{4}$' -InputObject {$_.Name} | Sort-Object | ForEach-Object {
    $year = $_
    Get-ChildItem -Directory $year | Select-String -Pattern '^\d{2}$' -InputObject {$_.Name} | Sort-Object | ForEach-Object {
        $month = (Join-Path $year $_)
        Get-ChildItem -Directory $month | Select-String -Pattern '^\d{2}$' -InputObject {$_.Name} | Sort-Object | ForEach-Object {
            $folder = (Join-Path $month $_)
            $files = Get-ChildItem -File $folder
            if ($files.Count -eq 0) {
                Write-Output "Day folder $folder contents (should be empty):"
                Write-Output (Get-ChildItem $folder)
                Remove-Item -Path $folder -Confirm
            }
        }
        $monthfiles = Get-ChildItem $month
        if($monthfiles.Count -eq 0) {
            Write-Output "Month folder $month contents (should be empty):"
            Write-Output $monthfiles
            Remove-Item -Path $month -Confirm
        }
    }
}