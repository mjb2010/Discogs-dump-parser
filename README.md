# Discogs-dump-parser
## A lightweight parser of Discogs data dumps

This software is released under a Creative Commons "CC0" Public Domain Dedication; see https://creativecommons.org/publicdomain/zero/1.0/ for more info.

Discogs artist, label, release and master release data is publicly available in huge XML files produced monthly and made available at https://data.discogs.com/ for anyone to download.

This little Python script parses the Discogs data using the ultrafast cElementTree parser which comes with Python 2.5 and up. The parsed data is mostly ignored; the idea is just to successfully read the XML, building a temporary tree for each 'release' element, and printing out a dot for every 1000 'release' elements read. At the end it tells you how much time it took. If you interrupt it, it tells you the last release ID it saw.

As of mid-2017, on my 3.1 GHz i5-2400 system (using one core), it takes 50 minutes to plow through the 4.6 GB gzipped release data XML, yet it only ever uses about 17 MB of memory. It could run faster if a temporary tree was not built and discarded for each 'release', but I feel it is a better benchmark this way.

To try it out, get one of the release data dump files, edit the script to define dump_filepath accordingly, and run the script. It automatically handles uncompressed files and the old style of dump which had no root element.
