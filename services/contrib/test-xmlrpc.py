#!/usr/bin/python

""" A XMLRPC Client

Arguments must follow this convention:
 - args are splitted over ';' (we call it an arg)

  => use --func myfunc --args "a;b;c" to request func('a', 'b', 'c')

 - in one arg, array/dict component are splitted over '|' (we call it a token)

  => use --func myfunc --args "a|b" to request func(['a', 'b'])

 - if an token contain '=', it is interpreted as a tuple

  => use --func myfunc --args "a=b|c=d" to request func(['a': 'b', 'c': 'd'])

 - if an token contain ',', it is interpreted as a list

  => use --func myfunc --args "a,b,c,d" to request func('a', 'b', 'c', 'd')

  => use --func myfunc --args "a,b|c,d" to request func(['a', 'b'], ['c', 'd'])
"""
 
import twisted.python.usage
import twisted.internet.reactor
import twisted.web.xmlrpc
import sys

class Options(twisted.python.usage.Options):

    optParameters = [
        ["func", None, None, "The XML RPC Function to use"],
        ["args", None, None, "The XML RPC Arguments to use, see below"],
        ["server", None, None, "The XML RPC server to contact, URI format"],
        ]


def _cb(result): # server do answer us
    print(result)
    twisted.internet.reactor.stop()
    return 0

def _eb(reason): # can't contact scheduler, log and continue
    print(reason)
    twisted.internet.reactor.stop()
    return 1

config = Options()
try:
    config.parseOptions()
except twisted.python.usage.UsageError, errortext:
    print '%s: %s' % (sys.argv[0], errortext)
    print '%s: Try --help for usage details.' % (sys.argv[0])
    sys.exit(1)

# parse cli args
args=[]
method = config["func"]
if config["args"]:
    args = config["args"].split(';')

parsedargs = []
for arg in args: # parse args
    tokenlist = arg.split('|')                     # split arrays args
    for token in tokenlist:                        # iterate over array content
        if token.count('=') == 1:                  # found a dict token
            (key, val) = token.split('=')          # process it
            try:
                items[key] = val
            except:
                items = {key: val}
	elif token.count(',') > 0:		   # found a list token
            try:
                items += [token.split(',')]
            except:
                items = [token.split(',')]
	elif token.count('~') == 1:		   # found a number
            try:
                items += int(token.split('~')[1])
            except:
                items = [int(token.split('~')[1])]
        else:                                      # found something else (simple value ?)
            try:
                items += token
            except:
                items = [token]

    if type(items) == type({}):
        parsedargs.append(items)
    elif type(items) == type([]):
        parsedargs += items
    else:
        parsedargs += items
    del(items)

twisted.web.xmlrpc.Proxy(config["server"]).callRemote(method, *parsedargs).addCallback(_cb).addErrback(_eb)
twisted.internet.reactor.run()
