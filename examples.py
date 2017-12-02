from loop import reactor
from loop import Deferred, inlineCallbacks
"""Test functions for deferreds"""
def f1(some, var):
	print('F1 executing with args %s, kwargs %s' % (some, var))

def f2(_, *args, **kwargs):
	for i in range(0, 10):
		print('Running')

def f3(_, *args, **kwargs):
	print('Another test')

def f4(_, *args, **kwargs):
	return Deferred(f5)

def get_arg(_, *args, **kwargs):
	print('Got args: %s' % _)

@inlineCallbacks
def f5(_, *args, **kwargs):
	print('Passing arguments to get_arg()')
	result = 'Value to pass'
	Deferred(get_arg, result).addErrback(error)
	return 'Returned from f5!'

def func_ret(*args, **kwargs):
	return 'Function return value'

@inlineCallbacks
def func_ret_(*args, **kwargs):
	return 'Function return value'

def badfunction():
	raise Exception('badfunction() error caught by errback')

@inlineCallbacks
def badfunction_():
	raise Exception('inline badfunction_() error caught by errback')

def show_result(result, *args, **kwargs):
	print(result)

def error(e):
	print(e)

"""inlineCallback"""
d = f5()
d.addCallback(show_result)

"""Error caught with errback"""
d = Deferred(badfunction)
d.addErrback(error)

"""Error caught with errback"""
d = badfunction_()
d.addErrback(error)

"""Callback chain example"""
d = Deferred(f1, "Test", "Function")
d.addCallback(f2)
d.addCallback(f3)
d.addErrback(error)

"""Return a value"""
d = Deferred()
d.addCallback(func_ret)
d.addCallback(show_result)
d.addErrback(error)

d = func_ret_()
d.addCallback(show_result)
d.addErrback(error)


reactor.fire_until_complete()