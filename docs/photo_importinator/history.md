---
layout: default
title: "Photo Importinator: History"
permalink: /photo_importinator/history.html
---

([Back to Photo Importinator](./))

# Photo Importinator: History

This is the *third* iteration of my photo import script.
It is frankly amazing that such a simple and mundane task
has required a *significant* amount of *mild* roadblocks
that had to be whacked apart.

## Primordial era

My photos used to live on local hard drive, but eventually,
the move to using a NAS was inevitable. By the time when I
moved my photos to my NAS for the first time, I was
using Adobe Photoshop Elements 14 Organizer.

Adobe software really is built on a small set of principles.
Among them:

1. We have certain *opinions* on how you should operate
   from now on when you use this software.
2. Don't you dare to use any other tools.
3. Don't you dare to touch the files I've touched yourself,
   or else.

Now, PSEO had this particular set of *opinions:* You can import
stuff from SD card real smooth. Importing from other sources?
Real jank. Oh and you can't trust the camera to put files in
DCIM folder. If you have an Android phone and you also use the
SD card to store app data, well, who knows, those 5000 random
image files *could* be your photographs, you know? Who knows!?
Be sure to make it clear, every time, which of these files
were yours and which were not. Mark them clearly. *Don't screw
up.* ...done importing? Cool! The application has declared your
files should be stored in NAS folders along the lines
of "YYYY MM DD". You don't need options. You'll thank us later.
You *can* move the files to subfolders manually, *if* you
allow the app to appear completely confused by your *audacity*
to move the files outside of the software, and let the app to
rescan and "reconnect" the files. *#JustAdobeThings*

...Anyway, having gotten enough fed up with this abusive
software, I moved away from PSEO to [digiKam][digiKam].
An application that is just cool.
Because it's *cool* with whatever way you choose to store
your photos on NAS. It has an importer of its own.
But if you don't want to use it, it's *cool*.
You see, digiKam *understands* that you might be mildly
traumatised by the shittiness of the importer in the
previous app you used, so it doesn't force you to use
its own. *It's cool. It's fine.* You can use your
own import tool if you want.

(Nowadays, I use [ACDSee Photo Studio][acdsee],
which is likewise *cool*. It has an importer too.
You also don't need to use it. *It's cool. It's fine.*
You can use your own import tool if you want. Also, the
cool thing is that these random pro tools *understand*
each other. If digiKam gets a lot better and more usable
and a lot faster, maybe I *will* switch back. Who knows!)

For a while after that, I just copied stuff over
with [`exiftool`][exiftool]. Not the perfect import process,
I guess. While it got the files moved, I needed more control.
And I wanted backups to be done automagically.
And NEF Raw files converted.

## Power Automate: A Tool for De-shenaniganisation

The very first PowerShell script was very rudimentary,
basically just running `exiftool` and `7za`.
So once things started to get more complicated, I first
made a Microsoft Power Automate script.
It worked for what it did, converting the raw files to DNGs
automatically and all that.

It was a bit janky, though not because of Power Automate.

Power Automate is an incredible piece of Windows technology. Mostly
because it can be used to easily script Windows application'
interactions, either through built-in support through Power Automate
("Hey, Excel, do this and that, plz"), or, failing that, you can just
control well-behaved, accessible pieces of software through clearly
defined actions ("Ok, we wait for window called Foo, then we click
a button that says Bar"). Failing *that,* it even provides dirty
tricks you can use against really thuggish applications that don't
give a darn about usability ("Activate a window that has *this*
complicated identifier, then wait until there's *this kind of
sub-picture* on screen somewhere, then click on *these window
coordinates* with left mouse button.")

Now, take a few guesses under which of these categories the
[Adobe DNG Converter][dngconv] falls under.

Yeah, Adobe DNG Converter should warrant a separate rant onto itself.
I mean, it *works.* It *does what it says.* That's the reason I
still keep it around. However, the user interface is *peculiar.* It
ostensibly has a command line interface, though it runs asynchronously,
thus making it completely unsuitable for use in scripts (though some
people apparently *janked it up* for PowerShell - I must admit I'm
not bold enough to try to use those scripts.)

Now, long story short: I had to stop using this approach, because
Adobe DNG Converted just stopped cooperating with the Power Automate
jank-o-vision. I have no idea why. Probably nothing to do with updates.
Probably everything to do with jank. *#JustAdobeThings*

Bottom line was this: stuff broke for good. Had to find an
alternate approach.

## PowerShell: It works... kinda?

The second iteration of the idea was a vast expansion of the
PowerShell script.

Rather than doing *some* parts of the work with the script,
at this point, I really wanted the script to do as many things
as possible.

You see, fundamentally, I'm a cheese-head. I can come up with a
complicated process, but if I don't write it down, I'll just
forget it. So it's better to just write a script that does as
much as possible, with as little instructions on my part as possible.
"Import stuff from Camera X." Stuff like that.

This was also an exercise in learning PowerShell and also my
first attempt at creating a non-trivial PowerShell script.

On the plus side, I found out about some neat features PowerShell
has, such as its own neat data file format which is sufficient for
most configuration data.

It worked reliably, and was not janky at all, actually.

I used it in conjunction with Adobe DNG Converter, but then I
later found [`dnglab`][dnglab], which does the conversion job
considerably more batch-processing-friendly than the Adobe tool.

So it works. What else do I want, you may wonder?

## Python: The true Power Tool era is upon us

Alas, even when PowerShell is in some regards more powerful than
traditional Unix shells, there's the old Unix adage that PowerShell
has not escaped from. "If you write a mega complex shellscript",
the greybeards say, "you end up wishing you wrote that in a *real*
scripting language."

So yeah. At some point the script grew to the point that I really
needed to throw some *actual software organisation* at it.

Basically, the script became a large mass of Stuff with little
real organisation. And while PowerShell can ostensibly do some fancy
complicated organisation of code, that's not really what I
use PowerShell for.

So I decided to rewrite it in Python. So now we're here.

The goals:

- Object-oriented modular design.
- The OOP design helps with:
  - Data gathering and reporting (Conversion status capture,
    conversion time stats, counting how many photos were
    taken on particular days, etc)
  - Eventual move/conversion parallelisation/queuing support
- Learning about neat new Python libraries. There's plenty
  of interesting Python modules that implement cool stuff.
  Many of them now built-in!
- Building a wider Python skillset for my future photography
  scripts! [Geoscooper](../geo_scooper/) was only the beginning.

## Distant future?

I dunno, maybe I'll end up being fed up with Python's multithreading
and I go mad and rewrite the whole bloody thing in Erlang or something.
But that is neither here or now!

[exiftool]: https://exiftool.org/
[dngconv]: https://helpx.adobe.com/camera-raw/using/adobe-dng-converter.html
[dnglab]: https://github.com/dnglab/dnglab
[digiKam]: https://www.digikam.org/
[acdsee]: https://www.acdsee.com/