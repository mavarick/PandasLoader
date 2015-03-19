#!/usr/bin/env python
#encoding:utf8

# io.py

import pdb
import sys
import traceback
import pandas as pd
import numpy as np

from decorators import add_doc
from decorators import cal_time



@add_doc(pd.read_csv)
def read_excel(filename, sheet_name=0, header=0, dtypes={}, **kargs):
    '''read excel by pandas.read_excel
    mainly parameters are listed below:

    parameters:
        filename
        sheetname  string or index, default is 0
        dtypes     use as conventers in pandas.read_excel()
                     be notice, func in conventers is applied on element
                     of data not columns
    dtypes functions:
        float       np.float/np.float64
        int         np.int/np.int64
        datetime    pd.to_datetime, used on single value with great power 
                        of intelligence. if arrays, should use pd.DatetimeIndex
    @to_datetime   pandas.to_datetime function is of great power to parse datetime
    @encoding      chinese characters will be encoded as 'unicode'

    for example:
        dtypes = {
            u'发生日期': pd.to_datetime
        }
        data = read_excel('test.xlsx', 0, dtypes=dtypes)
    '''
    data = pd.read_excel(filename, sheet_name=sheet_name, header=header, converters=dtypes)
    return data

@add_doc(pd.read_csv)
def read_csv(filename, header=0, encoding='utf8', sep=';', dtype=None, ftypes={}, 
        error_bad_lines=True, **kargs):
    ''' read csv file by pandas.read_csv
    @parameters:
        filename
        header      default is 0
        encoding    character encoding, chinese character in csv file from excel usually
                        is 'gb2312'
                    pandas raise errors when encoding is not right, and for chinese and korean,
                        'utf-16' is better for that
        sep         seperator or delimiter
        dtype       list or dict, specifying field types, see pandas.read_csv for usage
        ftypes      field type, existed for short of dtype, which only support np.dtypes and 
                        python type
        error_bad_lines  error 
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

@add_doc(pd.read_table)
def read_table(filename, sep='\t', header=0, encoding='utf-8', **kargs):
    ''' read txt table file by pd.read_table
    NOTICE:
        1, read_table is usually very faster than just reading csv
        2, but the encoding problems may occurs, so when writing to txt file, make sure
            which encoding character is used, like 'utf-16'

    @END
    '''
    data = pd.read_table(filename, sep=sep, header=header, encoding=encoding, **kargs)
    return data

''' dtype:
numpy methods
    int  np.int16, np.int32, np.int64
    float np.float, np.float32, np.float64
    datetime  np.datetime64

python buildin methods
    int
    float
    datetime.datetime

conventers:
pandas methods
'''
import pandas as pd
import numpy as np
dtypes = [
    # (field_name/field_index, type, default_value) 
    # if default_value is None, should be Nan in pandas
    ('id', np.int32, ''),
    ('name', str, ''),  # element should have type unicode
    ('amount', np.float32, 0.0),
    ('number', np.int32, 0),
    ('dtime', np.datetime64, None)
]


def handle_type(data, dtypes):
    ''' handle the data types
    '''
    assert type(data) == pd.DataFrame, "Error: data type must be pandas.DataFrame"
    error_num = 0
    error_lst = []
    
    for name, _dtype, default in dtypes:
        pdb.set_trace()
        try:
            data[name].astype(_dtype)
        except:
            pass
        else:
            continue
        if data[name].dtype is not _dtype:
            # array method
            try:
                data[name] = _dtype(data[name])
            except:
                pass
            else:
                continue
        # value method
        if data[name].dtype is not _dtype:
            try:
                data[name] = map(_dtype, data[name])
            except:
                pass
            else:
                continue
        # value error detection
        if data[name].dtype is not _dtype:
            col = data[name]
            for index in col.index:
                try:
                    col[index] = _dtype(col[index])
                except:
                    error_num += 1
                    error_lst.append((name, index, traceback.format_exc()))
        assert data[name].dtype == _dtype, \
            "Error: col[{0}] type should be {1}".format(name.encode('utf8'), _dtype)
    return error_num, error_lst

''' 
由于用户的写入问题导致导致的数据根本无法load进入到pandas，因此需要一个组件来对数据进行清理。
这个清理发生在load进入pandas之前，生成pandas能够处理的数据。
'''


'''
**Time Test**
for same data with different filetype:
    read_excel   xlsx   'gb2312'    470.611925125s
    read_table   txt    'utf-16'    8.74457001686s
    read_table   txt    None        6.82893490791s
    read_csv     csv    None        6.41652703285s
    read_csv     csv    gb2312      16.9414849281s
读取txt和csv格式的文件时间基本一致。但是编码的时间确实很多。
主要时间浪费在格式的转换上！


总结下来，其中的问题包括：
    1，字符编码问题
    2，字符类型/默认值问题；
    3，字符格式问题
'''

