"""
  parse_discogs_dump.py
  A lightweight parser of Discogs data dumps
  
  Version: 2018-09-30
  Original author: Mike J. Brown <mike@skew.org>
  License: CC0 <creativecommons.org/publicdomain/zero/1.0/>
  Requires: Python 2.5 or higher
"""

# for Python 2 compatibility
from __future__ import print_function

import gzip
from io import BytesIO
from sys import stdout, stderr, argv, exc_info

try:
	from xml.etree import cElementTree as ET
except ImportError:
	from xml.etree import ElementTree as ET
	print('cElementTree is not available; using regular ElementTree instead. Expect slowness.', file=stderr)

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
	Parse a release dump XML stream incrementally, fully removing elements
	when they are completely read, unless they are descendants of an element
	with the given name, in which case they are processed by the process()
	method of the given ElementProcessor (or subclass) instance.
	"""
	element_stack = []
	interesting_element_name = element_processor.interesting_element_name or 'release'
	interesting_element_depth = 0
	item_id = None
	try:
		context = ET.iterparse(stream, events=('start', 'end'))
		for event, elem in context:
			if event == 'start':
				element_stack.append(elem)
				if elem.tag == interesting_element_name:
					interesting_element_depth += 1
			elif event == 'end':
				element_stack.pop()
				if elem.tag == interesting_element_name:
					interesting_element_depth -= 1
					element_processor.process(elem)
				if element_stack and not interesting_element_depth:
					element_stack[-1].remove(elem)
		del context
	except:
		if hasattr(element_processor, 'handle_interruption'):
			element_processor.handle_interruption(exc_info()[0])
		else:
			print('\nInterrupted.', file=stderr)
			raise


class ElementProcessor:
	"""
	An object which processes ElementTree elements. Examples of subclasses follow.
	"""
	def __init__(self):
		self.counter = 0
		self.interesting_element_name = '' # subclasses should define this

	def process(self, elem):
		"""
		Do something with a parsed element.
		This example just increments a counter of elements processed.
		Subclasses should provide their own version of this method to do more.
		"""
		self.counter += 1

	def handle_interruption(self, e):
		"""
		If parsing is interrupted, this method will be called to handle it.
		This example prints the element count.
		"""
		print('\nInterrupted after %d %ss.' % (self.counter, self.interesting_element_name), file=stderr)
		raise


class ReleaseElementCounter(ElementProcessor):
	"""
	An example of an object which processes release elements:
	Print a dot for every nth release (default n=1000).
	If interrupted, print the parsed element count and last processed element ID.
	"""
	def __init__(self, n=1000):
		self.counter = 0
		self.item_id = None
		self.interval = n
		self.interesting_element_name = 'release'

	def process(self, elem):
		self.counter += 1
		self.item_id = elem.get('id')
		if self.counter % self.interval == 0:
			print('.', end='', file=stderr)
			stderr.flush()

	def handle_interruption(self, e):
		"""
		If parsing is interrupted, this method will be called to handle it.
		This example prints the element count.
		"""
		print('\nInterrupted after %d %ss. Last %s id parsed: %s' % (self.counter, self.interesting_element_name, self.interesting_element_name, self.item_id), file=stderr)
		raise


class ReleaseElementSerializer(ElementProcessor):
	"""
	Another example of an object which processes elements:
	Write an XML fragment to stdout for every nth release (default n=1000).
	If interrupted, do whatever the base class does.
	"""
	def __init__(self, n=1000):
		self.counter = 0
		self.interval = n
		self.interesting_element_name = 'release'

	def process(self, elem):
		self.counter += 1
		if self.counter % self.interval == 0:
			tree = ET.ElementTree(elem)
			tree.write(stdout, encoding='windows-1252')
			stdout.flush()
			del tree


def process_dump_file(dump_filepath, element_processor):
	"""
	Given an XML dump file path (as a string), convert it to a stream and
	pass it, along with anElementProcessor (or subclass) instance, to
	read_via_etree().
	"""
	dump_file_stream = GeneralEntityStreamWrapper(get_dump_file_stream(dump_filepath))
	read_via_etree(dump_file_stream, element_processor)
	dump_file_stream.close()


# when run from the command line, do this stuff
if __name__ == "__main__":
	from sys import argv
	from time import time
	if len(argv) < 2:
		raise RuntimeError("A dump file path must be provided as the first argument.")
	# for this demo, process the XML by printing a dot for every nth release element.
	processor = ReleaseElementCounter()
	# uncomment the following if you want an XML fragment instead of a dot
	#processor = ReleaseElementSerializer()
	print('reading file via cElementTree:', end='', file=stderr)
	stderr.flush()
	starttime = time()
	process_dump_file(argv[1], processor)
	endtime = time()
	print(' (total time: ', endtime - starttime, 's)', sep='', file=stderr)
