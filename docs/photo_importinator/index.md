---
layout: default
title: Photo Importinator
permalink: /photo_importinator/
---

# Photo Importinator

*It imports photos!  
This is suprisingly tricky and none of the apps I tried did it right!  
...So I wrote my own, dang it!*

## Overview

> "What mighty contests rise from trivial things."  
> —Alexander Pope

The intended audience of this software are people who host their
photographs locally on a NAS and use local digital asset
manager / photo management software (e.g. digiKam, ACDSee, what-have-you)
to access them.

The purpose of this script is as simple as this:

* Import images from SD card or locally auto-synced cloud drive
  (Dropbox, OneDrive, etc) to a NAS.
* During the import, perform conversion from camera-specific
  raw formats to DNG.
* Automatically create backup file of the original files (in case
  you ever need them again).

You may be asking why does this script exist at all.
Despite this being such a necessary and ubiquitous part of
photography workflow, and the fact that this feature also exists
on many DAMs too, *it might not work the way you expect it to.*
It's *surprisingly* easy to mess things up. I used
Adobe Photoshop Elements Organizer for a while, and I don't
want to relive that pain, thank you very much.

So, the aim is to minimise the user hassle and be flexible.

As a practical example: This is how I import images from my
camera to my NAS. I stick the SD card on my computer, and type

```console
> photo_importinator Nikon_D780
```

Simple, right?

But alas! Sometimes, Windows decides that the SD card should appear as `E:`
instead. Oh no, what will I do now?! Why, never despair:

```console
> photo_importinator --card E: Nikon_D780
```

...and on we go again!

The script allows for flexible configuration of the whole process,
with different settings for different cameras and different import targets.

## History

This is the *third* iteration of the same idea.

I originally had a Microsoft Power Automate script. It worked.
It was a bit janky, though not because of Power Automate.
I mostly used it because Adobe DNG Converter couldn't be scripted
otherwise. Then stuff broke for good. *#JustAdobeThings*

The second iteration was a PowerShell script. It worked
reliably, and was not janky at all, actually. Especially when I
decided to first convert the raw files to DNG manually, and
later found `dnglab` which does the job considerably more
batch-processing-friendly than the Adobe tool.

Just that at some point the script grew to the point that I really
needed to throw some actual software organisation at it. While
PowerShell can ostensibly do some fancy complicated organisation
of code, that's not really what I use PowerShell for.

Decided to rewrite it in Python. So now we're here.
