# Discogs-dump-parser
## A lightweight parser of Discogs data dumps

This software is released under a Creative Commons "CC0" Public Domain Dedication; see https://creativecommons.org/publicdomain/zero/1.0/ for more info.

Discogs artist, label, release, and master release data is publicly available in huge XML files produced monthly and made available at https://data.discogs.com/ for anyone to download.

This Python script parses the Discogs release data using the ultrafast [cElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html) API which comes with Python 2.5 and up. The script automatically handles compressed and uncompressed data, and the old style of dump which had no root element.

### Demo

To try it out, get one of the release data dump files and just run the script, passing the dump file path as the only argument. For example, if the script and the dump file named discogs_20191101_releases.xml.gz are in the same directory:

    python parse_discogs_dump.py discogs_20191101_releases.xml.gz

By default, a dot will be printed to the screen for every 1000 'release' elements read. At the end it tells you how much time it took. If you interrupt it, it tells you the last release ID it saw. The parsed data is mostly ignored; the idea is just to successfully read the XML, building a temporary tree for each 'release' element.

As of 2018, on my 3.1 GHz Intel Core i5-2400 system (using only 1 of 4 cores), it takes 61 minutes to plow through the 6.0 GB gzipped release data XML and print the dots, yet it only ever uses about 17 MB of memory. It could run faster if a temporary tree was not built and discarded for each 'release', but I feel it is a better benchmark this way.

If you uncomment one line of code near the end, then instead of a dot, you can get a complete XML fragment for every 1000th release element read.

### Customization

There is no need to modify parse_discogs_dump.py directly. You can write your own code to handle each 'release' element, which will be an instance of [`ElementTree.Element`](https://docs.python.org/2/library/xml.etree.elementtree.html#element-objects). Your code needs to just do the following:

1. Import `ElementProcessor` and `process_dump_file()` from parse_discogs_dump.py.
2. Define a subclass of `ElementProcessor` with, at a minimum, a `process()` method to handle each 'release' element (which will be an instance of `ElementTree.Element`) in whatever way you want.
3. Pass the dump file path and an instance of your subclass to `process_dump_file()`.

For example: [find_invalid_release_dates.py](https://pastebin.com/Acutu7xE) is a script which does exactly those things. It can be run like this:

    python find_invalid_release_dates.py discogs_20191101_releases.xml.gz > report.txt

Every time it finds a non-empty release date which does not match the patterns `####` or `####-##-##` with a non-zero month value, it will print a dot to the screen, and the output file report.txt will get a line like this:

    https://www.discogs.com/release/41748 - release date is "?"

### Contact

I am user [mjb](https://www.discogs.com/user/mjb) on Discogs. Feel free to contact me there via private message, or in the API forum.
