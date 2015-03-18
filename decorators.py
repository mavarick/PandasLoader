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

