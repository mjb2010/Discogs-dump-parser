"""
  parse_discogs_dump.py
  A lightweight parser of Discogs data dumps
  
  Version: 2018-09-26
  Original author: Mike J. Brown <mike@skew.org>
  License: CC0 <creativecommons.org/publicdomain/zero/1.0/>
  Requires: Python 2.5 or higher
"""

# for Python 2 compatibility
from __future__ import print_function

import gzip
from io import BytesIO
from sys import stdout, stderr
from time import time
from xml.etree import cElementTree as ET


# dump_filepath is the path to the dump file. It must end with '.xml' or '.xml.gz'.
dump_filepath = '''discogs_20180901_releases.xml.gz'''

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


def read_via_etree(stream, element_processor):
	"""
	Parse a release dump XML stream incrementally, fully removing elements when
	they are completely read, unless they are descendants of a 'release' element.
	
	Completed 'release' elements are handled by the process() method of an
	ElementProcessor subclass instance given as the 2nd argument.
	"""
	element_stack = []
	interesting_element_depth = 0
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
					release_id = elem.attrib['id']
					element_processor.process(elem)
				if element_stack and not interesting_element_depth:
					element_stack[-1].remove(elem)
		del context
	except:
		print('\nInterrupted. Last release parsed:', release_id, file=stderr)
		raise


class ElementProcessor:
	"""
	An object which processes elements. Examples of subclasses follow.
	"""
	def __init__(self):
		self.counter = 0

	def process(self, elem):
		"""
		Do something with a parsed element.
		This example just increments a counter of elements processed.
		Subclasses should provide their own version of this method to do more.
		"""
		self.counter += 1


class ReleaseElementProcessor(ElementProcessor):
	"""
	An example of an object which processes release elements.
	Prints a dot for every nth release, where n is global var 'interval'.
	"""
	def process(self, elem):
		self.counter += 1
		if self.counter % interval == 0:
			print('.', end='', file=stderr)
			stderr.flush()


class ReleaseElementSerializer(ElementProcessor):
	"""
	Another example of an object which processes elements.
	For every nth release, it writes an XML fragment to stdout.
	"""
	def process(self, elem):
		self.counter += 1
		if self.counter % interval == 0:
			tree = ET.ElementTree(elem)
			tree.write(stdout, encoding='windows-1252')
			stdout.flush()
			del tree


# when run from the command line, do this stuff
print('reading file via cElementTree:', end='', file=stderr)
stderr.flush()
dump_file_stream = GeneralEntityStreamWrapper(get_dump_file_stream(dump_filepath))
processor = ReleaseElementProcessor()
# uncomment the following if you want an XML fragment instead of a dot
#processor = ReleaseElementSerializer()
starttime = time()
read_via_etree(dump_file_stream, processor)
endtime = time()
dump_file_stream.close()
print(' (total time: ', endtime - starttime, 's)', sep='', file=stderr)
