---
layout: default
title: "Photo Importinator: Usage"
permalink: /photo_importinator/usage.html
---

([Back to Photo Importinator](./))

# Photo Importinator: Usage

## Terminology and basic premise

The Photo Importinator moves (or converts) files from a *source* to a *target*.

A *source* can be either

- an SD card (technically speaking, a local volume with a
  [DCIM][DCIM] folder), or
- a locally synced cloud drive (technically speaking, uh, any local folder
  will do, as you need to provide your own cloud syncing solution anyway).

A *target* is any folder that your computer/user has access to. Usually,
this is a NAS folder that is either mounted somewhere (in Windows, appears
as a drive letter) or is accessible through a locator (in Windows, accessible
through a server path *à la* `\\NAS-SERVER\photos`). Each target also has
a distinct way of organising files (e.g. "files in my NAS server should be
organised under `YEAR\MONTH\DAY` hierarchy").

### What is a camera, anyway, when you really think about it?

A *camera* is, well, a convenient label we give for a particular source of
photos. It's an internal label we use for settings for a particular scenario
when we move images from that particular source.

For example, I have a Nikon D780, and for the purposes of
using this program, I have decided to arbitrarily call it `Nikon_D780`.

The camera uses SD cards, which, when I put them to the SD card reader,
usually appear as drive `D:` on my computer. Whevever I format the
card on the camera (as I do after every import), the gamera gives the card
the volume label `NIKON D780`. The camera puts one file in the DCIM
folder, called `NC_FLLST.DAT`, which shouldn't be touched because none of
the software I have at hand knows a darn about it. Also, being a Nikon camera,
it uses `.NEF` raw files, which I prefer to be converted to the DNG format
automatically. Also, backups will be stored in vein of
`Nikon_D780_20241122.7z`, with the camera name and date stamp.

We can now express all of this information like this:

```toml
[Cameras.Nikon_D780]
card = 'D:'
card_label = 'NIKON D780'
ignore = [ 'NC_FLLST.DAT' ]
convert_raw = [ '.NEF' ]
```

And now whever I refer to my Nikon D780, I can just tell Photo Importinator
"I want photos from `Nikon_D780`, please". Or:

```console
> photo_importinator Nikon_D780
```

No need to tell where the files come from (usually - Windows may sometimes use
different drive letter, which can be overridden), no need to tell which files to
ignore, no need to tell which files to convert. Nice! And since I have a default
target set up, the one and only NAS I have, the importinator also knows where
the files and backups go.

So how do we configure the rest?

## Configuration file

The configuration file template is provides as `photo_importinator_config.example.toml`.
Copy the file to `photo_importinator_config.toml` in the appropriate configuration
directory, edit it appropriately as needed, and you're good to go.

### Location

The configuration directory is located in Local AppData in Windows
(`C:\Users\[you]\AppData\Local\photo_importinator\`). In
Windows Explorer, you can find it by entering `%AppData%`
in Explorer bar or `Win+R` dialog
(you end up in your Roaming AppData), navigating up,
and going to `Local` subfolder.

In Linux and other POSIXy systems, it is located in your
[XDG][xdg] configuration directory
(usually `~/.config/photo_importinator/`).

In both cases, you should create the `photo_importinator` folder
in case it doesn't exist, and why would it, if you haven't used the
app before - that'd be quite weird, right?

### The content

#### Backup

```toml
[Backup]
7zip_path = 'C:/Program Files/7-Zip/7z.exe'
```

This just specifies the path where your command-line
7-Zip executable lives. (The default value is just where the
64-bit Windows version lives.)

#### Target

```toml
[Target]
default = 'NAS-SERVER'

[Target.NAS-SERVER]
path = '//NAS-SERVER/photos'
backup_path = 'C:/Data/PhotoDump'
folder_structure = '{year:04d}/{month:02d}/{day:02d}'
```

The `Target` section defines the various targets where your files will end up in.
`default` specifies the default which you'll want to use; can be left
undefined or as `'None'` if you want no default to be set.

Folder structure: Use slashes `/` for path separation here, even in Windows.
The `{stuff in curly braces}` gets replaced by the number so named,
using uses [Python formatting rules][pyformat].
Long story short:
`:04d` in above template is "4-digit decimal, with leading zeros" and
`:02d` is "2-digit decimal, with leading zeros".
This is flexible enough if you want the folders to have names like
*2020 of the so-called Common Era/the month we counted as number 6/the day 10 of our monthly ordeal*
(why would you, though), but if you want, say, actual month names,
then this gets hella trickier.

Some simple examples:

- YYYY/MM/DD: `'{year:04d}/{month:02d}/{day:02d}'`
- YYYY-MM/DD: `'{year:04d}-{month:02d}/{day:02d}'`
- YYYY-MM: `'{year:04d}-{month:02d}'`

...I hope you get the idea.

Note how the target subsections are named in the configuration file. If you want your
target to be named `BLAH`, then the configuration should be in the section called
`[Target.BLAH]`. Same goes with the cameras below.

#### Conversion

```toml
[Conversion]
dnglab_path = 'dnglab.exe'
convert_flags = ['--dng-thumbnail', 'false']
```

This specifies the path to dnglab executable,
and the command-line flags given to the `convert` action.

#### Cloud

```toml
[Cloud]
Dropbox = 'Dropbox/Camera Uploads'
OneDrive = 'OneDrive/Pictures/Camera Roll'
```

These declare the *cloud sources*.
The paths are relative to home directory/folder.

#### Cameras

```toml
[Cameras]
default = 'None'

[Cameras.Nikon_D780]
card = 'D:'
card_label = 'NIKON D780'
ignore = [ 'NC_FLLST.DAT' ]
convert_raw = [ '.NEF' ]

[Cameras.Nokia]
card = 'OneDrive'
```

As with targets, the default camera can be specified here, or left as `'None'`.

For cameras, the only real required key is `card`. Just specify the drive letter
in Windows or mount point in POSIXland. Or, if it's a cloud source, just specify
which!

The `card_label` feature is not actually used anywhere, but one day I might
*(might!)* implement card auto-detection. Or at least some
verification doohickey. Just use whatever name the camera uses for the card
for now.

`ignore` is a list of files that should be ignored. (In this example, some
Nikon mystery data file.)

`convert_raw` should list which file extensions trigger the automatic DNG
conversion using dnglab.

## Using the script with Windows Terminal and PowerShell

You can add something like this to your PowerShell profile
(located at `C:\Users\[you]\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`):

```powershell
function photo_importinator {
  & python.exe "C:\whatever_folder_you_installed_this_on\photo_importinator\photo_importinator.py" $args
}
```

[DCIM]: https://en.wikipedia.org/wiki/Design_rule_for_Camera_File_system
[pyformat]: https://cheatography.com/brianallan/cheat-sheets/python-f-strings-number-formatting/
[xdg]: https://specifications.freedesktop.org/basedir-spec/latest/