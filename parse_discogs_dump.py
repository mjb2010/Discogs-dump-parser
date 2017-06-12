"""
  parse_discogs_dump.py
  A lightweight parser of Discogs data dumps
  
  Version: 2017-06-12
  Original author: Mike J. Brown <mike@skew.org>
  License: CC0 <creativecommons.org/publicdomain/zero/1.0/>
  Requires: Python 2.5 or higher
"""

# for Python 2 compatibility
from __future__ import print_function

import gzip, re
from io import BytesIO
from sys import stdout
from time import time
from xml.etree import cElementTree as ET


# dump_filepath is the path to the dump file. It must end with '.xml' or '.xml.gz'.
dump_filepath = '''I:\Downloads\discogs_20170601_releases.xml.gz'''

# interval affects how the progress of reading the file is marked.
# A dot will be displayed after that many releases have been read.
interval = 1000

### users do not need to modify anything below this line


class GeneralEntityStreamWrapper(object):
	"""
	A wrapper for an XML general parsed entity (an XML fragment which may or
	may not have a root/document element).
	
	Initialize it with the entity stream. It will act as if the stream is wrapped
	in an element named 'dummy'. It only supports read() and close() operations.
	"""
	_streams = None
	_current_stream = None

	def _prepare_next_stream(self):
		self._current_stream = self._streams.pop()
		self._read = self._current_stream.read
		self._close = self._current_stream.close

	def __init__(self, file_stream):
		self._streams = [BytesIO(b'</dummy>'), file_stream, BytesIO(b'<dummy>')]
		self._prepare_next_stream()

	def read(self, size=-1):
		if self._current_stream:
			bytes = self._read(size)
			if bytes:
				return bytes
			else:
				try:
					self._prepare_next_stream()
				except IndexError:
					return ''
				return self._read(size)
		else:
			return ''

	def close(self):
		self._close()


def get_dump_file_stream(filepath):
	"""
	Open the dump file, decompressing it on the fly if necessary.
	"""
	if filepath.endswith('.xml'):
		return open(filepath, 'rb')
	elif filepath.endswith('.xml.gz'):
		return gzip.open(filepath)
	else:
		raise 'Unknown extension on dump file path ' + dump_filepath


#for debugging, currently unused
def serialize(elem):
	"""
	Write out an XML fragment for the given element.
	"""
	tree = ET.ElementTree(elem)
	tree.write(stdout, encoding='windows-1252')
	stdout.flush()
	del tree


def read_via_etree(stream):
	"""
	Parse dump XML incrementally, fully removing elements when they are
	completely read, unless they are descendants of a 'release' element.
	
	'release' elements are handled specially, in this demo just printing
	a dot for every nth release, as determined by global var 'interval'.
	"""
	element_stack = []
	interesting_element_depth = 0
	release_counter = 0
	release_id = None
	try:
		context = ET.iterparse(stream, events=('start', 'end'))
		for event, elem in context:
			if event == 'start':
				element_stack.append(elem)
				if elem.tag == 'release':
					interesting_element_depth += 1
			elif event == 'end':
				element_stack.pop()
				if elem.tag == 'release':
					interesting_element_depth -= 1
					# after each release element is parsed, consider printing a dot
					release_id = elem.attrib['id']
					release_counter += 1
					if release_counter % interval == 0:
						print('.', end='')
						stdout.flush()
				if element_stack and not interesting_element_depth:
					element_stack[-1].remove(elem)
		del context
	except:
		print('\nInterrupted. Last release parsed:', release_id)
		raise


# when run from the command line, do this stuff
print('reading file via cElementTree:', end='')
stdout.flush()
dump_file_stream = GeneralEntityStreamWrapper(get_dump_file_stream(dump_filepath))
starttime = time()
read_via_etree(dump_file_stream)
endtime = time()
dump_file_stream.close()
print(' (total time: ', endtime - starttime, 's)', sep='')
