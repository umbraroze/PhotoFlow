---
layout: default
title: Photo Importinator
permalink: /photo_importinator/
---

([Back to PhotoFlow](../))

# Photo Importinator

*It imports photos!  
This is suprisingly tricky and none of the apps I tried did it right!  
...So I wrote my own, dang it!*

* Distributed under MIT license.
* [See code in GitHub](https://github.com/umbraroze/PhotoFlow/tree/master/photo_importinator).
* Complete rewrite in Python is underway; no official release as of yet.
* [Final "stable" PowerShell version](https://github.com/umbraroze/PhotoFlow/releases/tag/photoflow-powershell-final)
  is still available for download.

## Contents

* **[History](history.html)** &mdash; or why is this stuff so hard, and why does this script exist?
* **[Usage](usage.html)** &mdash; how to set up and configure the Photo Importinator

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
