---
layout: default
title: "Photo Importinator: History"
permalink: /photo_importinator/history.html
---

([Back to Photo Importinator](/photo_importinator/))

# History

This is the *third* iteration of the same idea.

## Power Automate

I originally had a Microsoft Power Automate script. It worked.
It was a bit janky, though not because of Power Automate.
I mostly used it because Adobe DNG Converter couldn't be scripted
otherwise. Then stuff broke for good. *#JustAdobeThings*

## PowerShell

The second iteration was a PowerShell script. It worked
reliably, and was not janky at all, actually. Especially when I
decided to first convert the raw files to DNG manually, and
later found `dnglab` which does the job considerably more
batch-processing-friendly than the Adobe tool.

## Python

Just that at some point the script grew to the point that I really
needed to throw some actual software organisation at it. While
PowerShell can ostensibly do some fancy complicated organisation
of code, that's not really what I use PowerShell for.

Decided to rewrite it in Python. So now we're here.
