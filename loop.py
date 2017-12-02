"""
Interesing take on a deferred model based on twisted.
The Reactor() loops through each deferred and calls 
one call back at a time until they are all consumed.
"""


class Reactor():
	def __init__(self):
		self._deferreds = []
		self.cur_def = 0
		self.running = True

	def addDeferred(self, deferred):
		self._deferreds.append(deferred)

	def _run(self):
		for deferred in self._deferreds:
			yield deferred

	def run(self):
		for deferred in self._run():
			deferred._fire()

	def fire_until_complete(self):
		while self.running:
			self.running = False
			for deferred in self._run():
				deferred._fire()
			for deferred in self._deferreds:
				if len(deferred._callbacks) > 0:
					self.running = True

class Deferred():

	def __init__(self, callable = None, *args, **kwargs):
		self._callbacks = []
		self._errback = None
		self._call_result = None
		self._result = None
		self._init   = False
		self._exist()
		if callable:
			self._callbacks.append((callable, args, kwargs))

	def __iter__(self):
		for i, callable in enumerate(self._callbacks):
			yield self._fire_args(callable)

	def _exist(self):
		reactor._deferreds.append(self)

	def _fire(self):
		if len(self._callbacks) > 0:
			callable = self._callbacks.pop(0)
			self._fire_args(callable)
			self._result = self._call_result
		return self._call_result

	def try_fire(f):
		def try_fire_call(*args, **kwargs):
			try:
				f(args[0], args[1])
			except Exception as e:
				if str(e) != 'ignore':
					args[0]._onerror(e)
		return try_fire_call

	@try_fire
	def _fire_args(self, callable):
		if not self._init:
			self._init = True
			self._call_result = callable[0](callable[1], callable[2])
		else:
			if callable[1]:
				self._call_result = callable[0](self._call_result, *callable[1], **callable[2])
			else:
				self._call_result = callable[0](self._call_result, *callable[1], **callable[2])

		if isinstance(self._call_result, Deferred):
			raise Exception('Warning: Deferred returned from a Deferred has an inaccessible result.')

	def addCallback(self, callable, *args, **kwargs):
		self._callbacks.append((callable, args, kwargs))
		return self

	def addErrback(self, callable):
		self._errback = callable

	def _onerror(self, e):
		self._errback(e)


def inlineCallbacks(f):

	def inline_callback(*args, **kwargs):
		return Deferred(f, *args, **kwargs)

	return inline_callback

"""You must define your event loop"""
reactor = Reactor()