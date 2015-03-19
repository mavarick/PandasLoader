#!/usr/bin/env python
#encoding:utf8

import pdb
''' use the doc for new functions
'''
def add_doc(origin_func):
    def _wrapper(add_func):
        add_func.__doc__ = '\n'.join(map(str, [
                add_func.__doc__,
                ' * '*5 + "ORIGIN DOC" + ' * ' * 5,
                origin_func.__doc__
            ]))
        return add_func
    return _wrapper

import time
def cal_time(func):
    def wrapper(*args, **kargs):
        st = time.time()
        func(*args, **kargs)
        et = time.time()
        print "Time Consumed: {0}s".format(et - st)
    return wrapper

'''
USAGE:
    add 'default_val' kwd argument for function

EXAMPLE:
def test_add_args():
    def foo(val, default_val):
        print "default: ",default_val
    boo = add_args(foo, default_val=100)
    print boo(1000)
'''
def add_args(parse_func, default_val):
    def parser(*args):
        return parse_func(*args, default_val=default_val)
    return parser



