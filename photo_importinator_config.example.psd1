# This is an example of a configuration file for photo_importinator.ps1 script.
# Put this in $HOME\Documents\WindowsPowerShell\photo_importinator_config.psd1
@{
    Tools = @{
        SevenZip = 'C:\Program Files\7-Zip\7z.exe'
        Exiv2 = 'exiv2.exe'
    }
    Backup = "C:\Data\PhotoDump"
    Destination = "\\NAS-SERVER\photos"
    FolderStructure = '{0:yyyy}/{0:MM}/{0:dd}'
    Cameras = @{
        "Nikon_D780" = @{
            Card = "D:"
            CardLabel = "NIKON D780"
            Ignore = @("NC_FLLST.DAT")
        }
        "Nokia_5" = @{
            Card = "Dropbox"
        }
    }
}