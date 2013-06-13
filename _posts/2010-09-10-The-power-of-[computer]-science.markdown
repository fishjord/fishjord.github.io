---
layout: post
title:  "The power of [computer] science!"
date:   2013-05-09 18:59:21
categories: misc
---

#Or: Recovering data from a formatted (Xbox 360) hard drive.

First we need to understand that in order to delete something you have to overwrite it several times with random bit patterns.  In reality 'delete' means nothing more than the space that file occupies is marked as free.  The actual 1s and 0s of the file still exist on the drive, intact, until they are over written.

Next we need to know that when a drive is formatted all that happens is a bunch of accounting information is written to the drive, there is no overwriting of any file data...probably, the xbox 360 drive is an extremely simple case, other file systems allow you to vary the block size [smallest amount of space a 'file' can occupy] and other variables that effect where accounting information is written, but if you reformat a drive using the exact same specifications all that should happen is the accounting information is overwritten and your files get unlinked (aka the file system doesn't know they exist anymore).  The 1s and 0s of the file still exist on the drive however.

Using this information I was able to salvage all of my saves from the drive.

So you want to recover your xbox 360 saves from your formatted hard drive (or you just want to know how it is possible, that's cool too).  This is -not- for the faint of heart, most of the steps are fairly benign, but some can really cause damage to your xbox 360 hard drive and as always, you are responsible for whatever you do, this is just a recap of how I managed to recover my saves.  It may or may not work for you.

## What you'll need:
Some way to connect your xbox 360 hard drive to your computer (Data Migration Kit [significantly cheaper], Xport360 [also supports xbox memory cards])
Xport360 software (http://uk.codejunkies.com/support/article.aspx?article_id=272)
FileFinder.java (written by me)
check_potential_files.py (written by me)
extract360.py (ftp://rene-ladan.nl/pub/distfiles/extract360.py by Rene Ladan)

## Getting the Disk Image
The first thing we need to do is get an exact copy of the bits on the hard drive (this will require the same amount of free space on your computer as the size of your xbox 360 hard drive, in my case 120 gigs).  There are several ways to do this.  Xport360 has a backup option that will create an exact image of your drive and save it to a file; however I never got it to work.  Xplorer360 did work for me, however it is a pain to get working, you need to download a copy of the mscvr71.dll to and place it in your system directory (vista/win7).  That being said it did work.  The method that I settled on was using a linux staple tool dd.  Hooked the drive up to my linux box and used the command 'dd if=/dev/sd[a/b/c/d/e/f/g] of=xbox_image.bin bs=4096' to copy the bits to the file xbox_image.bin.

## Identifying Potential Files
With the drive image in hand I had to figure out how exactly to find potential files on the hard drive.  As luck would have it the good people at http://free60.org/ have a great homebrew wiki up that has detailed descriptions of the xfat file system and file container format.  The take away was that any file we're interested in the first 4 bytes will be either 'CON ' 'LIVE' or 'PIRS'.  Through trial and error I was also able to determine that the files are aligned to a 4 byte boundary (really in retrospect that would have been a safe assumption, but you never know).  Now I just needed a way to process this huge 120 gig file and record every location where CON  LIVE or PIRS occurs.  Easy right?

My first attempt at that was in python, which was great, it was easy to experiment with, however it just was too slow since you can't read the bit patterns directly, you have to read them in to strings then unpack them and python doesn't handle io buffering so you have to do it yourself (~60 times speed up if you pick the right buffer size, or a 60 times slowdown if you pick the wrong buffer size).  I found with buffer size of 1 it took 33 seconds to read 100mb, with buffer size 1024 it took .2 seconds and with buffer size 4096 it took .05 seconds.

Anyway, this wasn't really acceptable so once I had worked out all the kinks (I did a lot of trial and error to figure out things, and the python script was immensely helpful with that) I recoded it in java.  Less than 50 lines of code and I had myself a fast, fairly accurate xfat file detector.

Finally to identify potential files I ran my java program (it writes potential file locations as offsets from fileloc 0 to stdout), redirect stdout to a file, and then let it run.  It processed the entire 120gig disk image file in a little under 55 minutes.  Compared to the python script that I let run for 24 and it didn't finish...<Sigh>

Checking to see which are real files
So now we have a file that has a list of the locations of all the potential files in the xbox 360 disk image.  In order to figure out which ones are real we need to use a bit of understanding gleaned from free360.org.  Every xbox360 file has a sha1 hash embedded in it that is a hash of  the bytes from 0x0344-0x[A-B]000 depending on if the file is CON or LIVE/PIRS.  So we can do a simple has check and if it fails we assume it isn't a real file, if it passes we've got a real file!  Woo!

Another useful tidbit from free60.org is information about the content type bytes.  Every file has an or'ed 4 byte bit pattern that specifies what type(s) the file is, and one of those types is Game save!

## Identifying your saves
Now once you've run the check_potential_files.py you'll have a bunch of files and folders in the current working directory (with names like file<number>.bin file<number>.bin.txt file<number>.bin.dir and some pngs.  Where it gets a bit tricky is trying to figure out which of these files are your game saves.  There are some hints in the file<number>.bin.txt (this file is basically a plain text dump of the.

Some useful tidbits I've found are that for every game a save directory is created.  This directory will have two pngs (one 64x64, one 32x32) and contain a save for that game.  The easiest way to identify a save directory is to look at the pngs that come out for the right save directory; they should be fairly recognizable.

One truly annoying thing is as far as I can tell the files don't quite encode their length in them, so the script just takes a guess and copies 4 mb from the disk image in to the bin file.  For most saves this should be enough (my ffxiii saves are all .3-1mb each).  So some trimming may be required.

## Getting your saves back on the drive

So now you have your saves in files and you want to actually use them!  We'll need the Xport360 software again.  If you're using win7 like I am you might have trouble copying files to the drive; the fix they suggest is disabling UAC which worked for me.

We'll use my FFXIII saves as an example for this, because that was the one I am most interested in at this point.  I'll update again once I figure out how to restore my mass effect 1&2 saves and orange box saves (I loves me my portal and I still have some challenges to complete damn it).

The first thing I tried was to copy the file straight on to the drive.  That didn't work so well, it ended up thinking it was a corrupted save.  So next I started a new FFXIII game and played to the first save point, saved and then looked at the folders in Xport to try and discern the structure.  That helped, I managed to figure out that in the gamer profile directory (read the Xport manual pdf for a great primer on the file layout of the xbox 360 hard drive) there was one folder for ffxiii which had one sub directory named 0000001, and inside was ff13-00.dat (save 1).  

With that I was able to figure out the structure, and knowing the size (~330kb) I knew my file was too big so I decided to peek in to my ff13-17 save and try to trim it down a bit.  I was lucky enough to find a second instance of CON in it, so I knew that was the start of a new file.  So I just deleted everything after that (include the CON ).  I renamed the file to ff13-17.dat (probably doesn't matter, especially since the saves start count at 0 so my save should have really been ff13-16.dat, but I just wanted to keep the naming consistent) and copied it over to the 0000001 directory on the drive.

I slide the drive back in the 360, started it up, and boom it recognized the save.

I'm so esctatic that I can barely see straight.  Or perhaps that's sleepy.  Or maybe it is something else entirely.  Whatever the case may be, I'm pretty damn pleased with the way things turned out!


