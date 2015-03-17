#!/usr/bin/env python
#encoding:utf8

import pdb
''' use the doc for new functions
'''
def add_doc(origin_func):
    def _wrapper(add_func):
        add_func.__doc__ = '\n'.join([
                add_func.__doc__,
                ' * '*5 + "ORIGIN DOC" + ' * ' * 5,
                origin_func.__doc__
            ])
        return add_func
    return _wrapper


