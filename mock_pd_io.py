#!/usr/bin/env python
#encoding:utf8

# demo for reading data
import pdb
import pandas as pd 
import numpy as np
from pd_io import read_csv, read_table, read_excel

## for csv file
filename = '/Users/apple/Documents/privates/tools/temp/mock.csv'
filename = '/Users/apple/Documents/privates/tools/temp/mock.txt'
filename = '/Users/apple/Documents/privates/tools/temp/mock.xlsx'
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

def to_float32(target_val):
    try:
        new_val = np.float32(target_val)
        if pd.isnull(new_val): new_val = None
    except:
        return None
    return new_val

dtypes = [
    # (field_name/field_index, type, func, default_value) 
    # if default_value is None, should be Nan in pandas
    # and type should always be numpy types
    # str or unicode type will transformed to 

    ('id', np.int32, np.int32,  ''),
    ('name', unicode, unicode, ''),  # element should have type unicode
    ('amount', np.float32, to_float32, 0.0),
    ('number', np.float64, np.float64, 0.0),
    #('dtime', np.datetime64, pd.to_datetime, None)
    ('dtime', pd.Timestamp, pd.to_datetime, None)
]

dtyps = [
    {"name":"id"},
    {"name":"name"},
    ('amount', np.float32, to_float32, 0.0),
    {"name":'number', "type":np.float32, "default": 0.0},
    {"name":'dtime', "type": pd.Timestamp, "parser":pd.to_datetime, "deafult": None}
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

#read csv
#data = read_csv(filename, encoding='gb2312', dtypes=dtypes, na_values={"number":['']},
#    transform=0, parse_on_loading=1, check_after_load=1)
#read txt
#data = read_table(filename, encoding='gb2312', dtypes=dtypes, na_values={"number":['']},
#    parse_on_loading=1, check_after_load=1)

data = read_excel(filename, 0, dtypes=dtypes)
print data

