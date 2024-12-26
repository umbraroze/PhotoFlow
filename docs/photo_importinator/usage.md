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

[DCIM]: https://en.wikipedia.org/wiki/Design_rule_for_Camera_File_system