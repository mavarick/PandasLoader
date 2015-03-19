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
from decorators import add_args

'''
Notes
-----
1. null values and wrong values should be NaN
2. converter function has format: convert_func(element, default_value)
3. dtype should be np dtypes. which contains:
    np.str, np.unicode
    np.int16, np.int32, np.int64
    np.float, np.float32, np.float64
    np.datetime64
4, Time test for `read_excel`/`read_csv`/`read_table` in pandas
for same data with different filetype:
    read_excel   xlsx   'gb2312'    470.611925125s
    read_table   txt    'utf-16'    8.74457001686s
    read_table   txt    None        6.82893490791s
    read_csv     csv    None        6.41652703285s
    read_csv     csv    gb2312      16.9414849281s
读取txt和csv格式的文件时间基本一致。但是编码的时间确实很多。
主要时间浪费在格式的转换上！
5, The Main problems when loading data
总结下来，其中的问题包括：
    1，字符编码问题
    2，字符类型/默认值问题；
    3，字符格式问题
6, CHECK_T
when data is loaded into DataFrame, program will check the data type for eath 
column of dataframe. but circumstances happend on some certain data type which
 will be changed in loading, `CHECK_T` is dict for it
'''

CHECK_T = {
    np.datetime64: np.dtype('<M8[ns]'),
    str: np.dtype('O')
}

def parse_dtypes(dtypes):
    ''' parse the dtyps list, generate different parts of arguments for pandas read_csv/table functions
    '''
    dtype = {}
    parse_dates = []
    default_value_dict = {}
    converters = {}
    num = 0
    for index in range(len(dtypes)):
        index_or_name, _t, default_value = dtypes[index]
        # handle default values, when the value is NaN, then fillit
        if default_value is not None:
            default_value_dict[index_or_name] = default_value
        # converters
        if _t.__name__ not in np.__dict__:
            converters[index_or_name] = _t
            continue
        # parse_dates
        if _t in [np.datetime64]:
            parse_dates.append(index_or_name)
            continue
        # dtype
        dtype[index_or_name] = _t
    return dtype, parse_dates, converters, default_value_dict

def check_ser_type(ser, dtype):
    ''' check series has dtype or not
    '''
    #pdb.set_trace()
    def check_type():
        try:
            return ser.dtype == dtype or type(ser[0]) == dtype
        except:
            return False

    #pdb.set_trace()
    error_list = []
    if not check_type():
        try:
            ser.astype(dtype)
        except:
            pass
    if not check_type():
        try:
            new_ser = dtype(ser)
            if new_ser and len(new_ser) == len(ser):
                ser = new_ser
        except:
            pass
    if not check_type():
        try:
            for idx, item in enumerate(ser):
                ser[idx] = dtype(item)
        except:
            pdb.set_trace()
            error_list.append((idx, item, dtype))
    return ser, error_list

@add_doc(pd.read_csv)
def read_excel(filename, sheet_name=0, header=0, dtypes={}, **kargs):
    '''read excel by pandas.read_excel

    Parameters
    ----------
    filename: string
    sheetname:string or int, default is 0
    dtypes: list, dict. TODO
    encoding: string

    TODO
    ----
    1. use dtypes to convert field after loading data

    '''
    data = pd.read_excel(filename, sheet_name=sheet_name, header=header, converters=dtypes)
    return data

#@add_doc(pd.read_csv)
def read_csv(filename, header=0, encoding='utf8', sep=';', dtypes = {},error_bad_lines=True, 
        parse_on_loading=1, check_after_load=1,
        **kargs):
    '''read csv file by pandas.read_csv

    Parameters
    -----------
    filename: string
    parse_on_loading: int, bool
        =1, parsing when loading; =0, not parsing 
        pandas buildin data parser is very great. if want to use it, parse_on_loading should be 1
    check_after_load: int, bool
        =1, checking after load; =0, not checking
        (parse_on_loading=1, check_after_load=1)  most robust method for loading
        (parse_on_loading=1, check_after_load=0)  recommand way
                
        (parse_on_loading=0, check_after_load=1)  for error data detection
        (parse_on_loading=0, check_after_load=0)  load without parsing, all is Object('O')
    header: int
        set header row index, see pandas.read_csv
    encoding: string. like 'gb2312'/'utf-16' for chinese, 
        character encoding, chinese character in csv file from excel usually is 'gb2312'
        pandas raise errors when encoding is not right, and for chinese and korean,
            'utf-16' is better for that
    sep: string
    dtype: list or dict, also see: pandas.read_csv
    error_bad_lines: bool. 
        default is False, meaning skip bad lines, whicn contains more or less elements

    Returns
    ------
    data: pandas.DataFrame 

    Examples
    --------
    # define convertion function
    def to_float32(target_val, default_val):
    try:
        new_val = np.float32(target_val)
    except:
        new_val = default_val
    return new_val

    #define dtypes
    dtypes = [
        # (field_name/field_index, type, default_value) 
        # if default_value is None, should be Nan in pandas
        # and type should always be numpy types
        ('id', np.int32, ''),
        ('name', unicode, ''),  # element should have type unicode
        ('amount', to_float32, 0.0),
        ('number', np.int32, 0),
        ('dtime', np.datetime64, None)
    ]
    # read file
    data = read_csv(filename, encoding='gb2312', dtypes=dtypes, 
        parse_on_loading=1, check_after_load=1)

    Notes
    -----
    1, encoding is one annoying problems in data reading
    2, pandas use ser.astype(type) to transform the value to specifed types
    3, np.int should be replaced as np.float, for NaN problems

    Also see 
    --------
    http://pandas.pydata.org/pandas-docs/stable
    or 
    help(pandas.DataFrame.read_csv)
    '''
    # read data
    dtype, parse_dates, converters, default_value_dict = parse_dtypes(dtypes)
    if parse_on_loading == 1:
        data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep, 
            dtype=dtype, parse_dates=parse_dates, converters = converters,
            error_bad_lines=error_bad_lines)
    else:
        data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep,
            error_bad_lines=error_bad_lines)
    #pdb.set_trace()
    # check data
    if check_after_load:
        for index_or_name, _t, default_value in dtypes:
            check_t = CHECK_T.get(_t, _t)
           
            ser, error_list = check_ser_type(data[index_or_name], check_t)
            if error_list:
               print "Error Data: {0}, info: {1}".format(index_or_name, error_list)
    # fillna
    for index_or_name, default_val in default_value_dict.iteritems():
        data[index_or_name].fillna(default_val, inplace=True)
    #
    return data

#@add_doc(pd.read_table)
def read_table(filename, sep='\t', header=0, encoding='utf-8', 
        parse_on_loading=1, check_after_load=1,
        **kargs):
    ''' read txt table file by pd.read_table

    Also see
    --------
    read_csv(), the only difference with read_csv() is sep, that's why new version 
    pandas hasn't list this function
    '''
    return read_csv(filename, sep=sep, header=header, encoding=encoding,
        parse_on_loading=parse_on_loading, check_after_load=check_after_load,
        **kargs)

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





