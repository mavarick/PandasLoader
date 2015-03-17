#!/usr/bin/env python
#encoding:utf8

# io.py

import pdb
import pandas as pd
import numpy as np

from lib import add_doc

def read_excel(filename, sheetname, fields={}, **kargs):
    '''read excel by pandas.read_excel
    mainly parameters are listed below:

    parameters:
        filename
        sheetname  string or index, default is 0
        fields     use as conventers in pandas.read_excel()
                     be notice, func in conventers is applied on element
                     of data not columns
    fields functions:
        float       np.float/np.float64
        int         np.int/np.int64
        datetime    pd.to_datetime, used on single value with great power 
                        of intelligence. if arrays, should use pd.DatetimeIndex
    @to_datetime   pandas.to_datetime function is of great power to parse datetime
    @encoding      chinese characters will be encoded as 'unicode'

    for example:
        fields = {
            u'发生日期': pd.to_datetime
        }
        data = read_excel('test.xlsx', 0, fields=fields)
    '''
    if not sheet_name: sheet_name=0  # the first sheet
    data = pd.read_excel(filename, sheet_name, header=header, converters=fields)
    return data

@add_doc(pd.read_csv)
def read_csv(filename, header=0, encoding='utf8', sep=';', dtype=None, ftypes={}, **kargs):
    ''' read csv file by pandas.read_csv
    @parameters:
        filename
        header      default is 0
        encoding    character encoding, chinese character in csv file from excel usually
                        is 'gb2312'
        sep         seperator or delimiter
        dtype       list or dict, specifying field types, see pandas.read_csv for usage
        ftypes      field type, existed for short of dtype, which only support np.dtypes and 
                        python type
    notices:
        1, encoding is one annoying problems in data reading
        2, pandas use ser.astype(type) to transform the value to specifed types. 
            but pd.Timestamp does not work at all, we should use DatatimeIndex(col)
            this could cause very bad experiences!
            look up doc, type should only be 'numpy.dtype or Python type' !
    examples:
        dtype={
            u'发货额(扣信息费)': np.float32,
            u'件数': int,
        }
        ftype={
            u'日期': pd.DatetimeIndex,
            u'月份': pd.DatetimeIndex
        }
    data = read_csv(filename, header=0, dtype = dtype, ftypes=ftypes, encoding='gb2312')
    @END
    '''
    data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep, 
            dtype=dtype, **kargs)
    for key, ftype in ftypes.iteritems():
        data[key] = ftype(data[key])
    return data

def test_read_csv():
    filename = "temp/test.csv"
    dtype={
            u'发货额(扣信息费)': np.float32,
            u'件数': int,
        }
    ftypes={
            u'日期': pd.DatetimeIndex,
            u'月份': pd.DatetimeIndex
        }

    data = read_csv(filename, header=0, dtype = dtype, ftypes=ftypes, encoding='gb2312')
    print data
    



