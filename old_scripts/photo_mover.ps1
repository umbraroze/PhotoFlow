echo "About to move images from `"Incoming`" to YYYY/MM/DD. Ctrl+C to abort."
Pause
& exiftool.exe -r "-Directory<DateTimeOriginal" -d "%Y/%m/%d" Incoming
