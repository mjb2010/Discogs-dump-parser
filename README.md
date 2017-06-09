# Discogs-dump-parser
## A lightweight parser of Discogs data dumps

This software is released under a Creative Commons "CC0" Public Domain Dedication; see https://creativecommons.org/publicdomain/zero/1.0/ for more info.

Discogs artist, label, release and master release data is publicly available in huge XML files produced monthly and made available at https://data.discogs.com/ for anyone to download.

This little Python script parses the Discogs data using the ultrafast cElementTree parser which comes with Python 2.5 and up. The parsed data is mostly ignored; the idea is just to successfully read the XML as fast as possible and print out a dot for every 1000 'release' elements read. At the end it tells you how much time it took. If you interrupt it, it tells you the last release ID it saw.

To try it out, get one of the release data dump files (they are huge!), edit the script to define dump_filepath accordingly, and run the script. The dump file can be left gzipped or it can be unzipped; the script handles it either way.
