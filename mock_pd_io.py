#!/usr/bin/env python
#encoding:utf8

# demo for reading data
import pdb
import pandas as pd 
import numpy as np
from pd_io import read_csv

## for csv file
filename = '/Users/apple/Documents/privates/tools/temp/mock.csv'
'''
names = ['id', 'name', 'amount', 'number', 'dtime']
dtype = {
    "id": np.int64,
    "name": str,
    "amount": np.float32,
}
parse_dates = ['dtime']
encoding='gb2312'
na_values={
    'amount': []
}
'''

def to_float32(target_val, default_val):
    try:
        new_val = np.float32(target_val)
    except:
        new_val = default_val
    return new_val


dtypes = [
    # (field_name/field_index, type, default_value) 
    # if default_value is None, should be Nan in pandas
    # and type should always be numpy types
    # str or unicode type will transformed to 

    ('id', np.int32, ''),
    ('name', unicode, ''),  # element should have type unicode
    ('amount', to_float32, None),
    ('number', np.float64, 0),
    ('dtime', np.datetime64, 0)
]

'''
dtypes = [
    (0, np.int32, 0),
    (1, str, ''),  # element should have type unicode
    (2, to_float32, None),
    (3, np.int32, 0),
    (4, np.datetime64, None)
]
'''


data = read_csv(filename, encoding='gb2312', dtypes=dtypes, na_values={"number":['']},
    transform=0, parse_on_loading=1, check_after_load=1)


print data

