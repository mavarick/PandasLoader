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
CHECK_T
when data is loaded into DataFrame, program will check the data type for eath 
column of dataframe. but circumstances happend on some certain data type which
 will be changed in loading, `CHECK_T` is dict for it
'''
CHECK_T = {
    np.datetime64: np.dtype('<M8[ns]'),
    str: np.dtype('O'),
    unicode: np.dtype('O'),
}

def parse_dtypes(dtypes):
    ''' parse the dtyps list, generate different parts of arguments for pandas read_csv/table functions
    '''
    dtype = {}
    parse_dates = []
    default_value_dict = {}
    converters = {}
    field_names = []
    num = 0
    for index in range(len(dtypes)):
        index_or_name, _t, _func, default_value = dtypes[index]
        field_names.append(index_or_name)
        # handle default values, when the value is NaN, then fillit
        if default_value is not None:
            default_value_dict[index_or_name] = default_value
        # converters
        if _func.__name__ not in np.__dict__:
            converters[index_or_name] = _func
            continue
        # parse_dates
        if _t in [np.datetime64]:
            parse_dates.append(index_or_name)
            continue
        # dtype
        dtype[index_or_name] = _t
    return dtype, parse_dates, converters, default_value_dict, field_names

def check_ser_type(ser, dtype, parse_func):
    ''' check series has dtype or not
    '''
    pdb.set_trace()
    def check_type():
        try:
            return ser.dtype == dtype or type(ser[0]) == dtype
        except:
            return False

    error_list = []
    if not check_type():
        try:
            ser.astype(dtype)
        except:
            pass
    if not check_type():
        try:
            new_ser = parse_func(ser)
            if new_ser and len(new_ser) == len(ser):
                ser = new_ser
        except:
            pass
    if not check_type():
        try:
            for idx, item in enumerate(ser):
                ser[idx] = parse_func(item)
        except:
            pdb.set_trace()
            error_list.append((idx, item, dtype))
    return ser, error_list


DEFAULT_TYPE=unicode
DEFAULT_PARSER=unicode
DEFAULT_VALUE=None
TYPE_DEFAULT_VALUE={
    unicode: '',
    # others: None
}
TYPE_DEAFULT_PARSER={
    unicode:unicode,
}
def parse_field_format(field_item):
    '''parse input field

    just for convinience

    Parameters
    ----------
    field_item: tuple with length 1/2/3/4
        field_item is of type tuple:
        complete format is (field_name, type, parser, default), for convinience, defile:
        :(name, ) : with type/parser are all np.unicode, and default_val is None
        :(name, type, ): with parse_func = type, and default is None
        :(name, type, parser, ): with default is None
        or of type dict:
        {"name": name, 'type'=type, 'parser': parser, 'default':default_val}
        :{"name": name}: type/parser='unicode', default is None
        :{"name": name, "default":default}: type/parser = unicode
        :{"name": name, "type": type, "default":default}: parser=type

    Returns
    -------
    (name, type, parser, default)
        the complete format

    Notes
    -----
    1, default value of unicode type is ''
    '''
    if type(field_item) in [dict]:
        name = field_item.get('name')
        field_type = field_item.get('type', unicode)
        field_parser = field_item.get("parser", unicode)
        default = field_item.get("default", TYPE_DEFAULT_VALUE.get(field_type, None))
    elif type(field_item) in [list, tuple]:
        args_number = len(field_item)
        if args_number == 1:
            name = field_item[0]
            field_type = DEFAULT_TYPE
            field_parser = TYPE_DEAFULT_PARSER.get(field_type, DEFAULT_PARSER)
            default = TYPE_DEFAULT_VALUE.get(field_type, DEFAULT_VALUE)
        elif args_number == 2:
            name, field_type = field_item
            field_parser = TYPE_DEAFULT_PARSER.get(field_type, DEFAULT_PARSER)
            default = TYPE_DEFAULT_VALUE.get(field_type, DEFAULT_VALUE)
        elif args_number == 3:
            name, field_type, field_parser = field_item
            default = TYPE_DEFAULT_VALUE.get(field_type, DEFAULT_VALUE)
        elif args_number == 4:
            name, field_type, field_parser, default = field_item
            if field_parser == None: field_parser = field_type
        else:
            raise (Exception, "Error: Arguments Number is out of [1, 2, 3 4]")
    else:
        raise (Exception, "Error: Field Type must be dict/list/tuple")
    return (name, field_type, field_parser, default)

#@add_doc(pd.read_csv)
def read_excel(filename, sheet_name=0, header=0, dtypes={}, **kargs):
    '''read excel by pandas.read_excel

    Parameters
    ----------
    filename: string
    sheetname:string or int, default is 0
    dtypes: list, dict. TODO
    encoding: string
    '''
    # read the data
    data = pd.read_excel(filename, sheet_name=sheet_name, header=header)
    # check the data
    for field_item in dtypes:
        index_or_name, _t, _func, default_value = parse_field_format(field_item)
        check_t = CHECK_T.get(_t, _t)
           
        ser, error_list = check_ser_type(data[index_or_name], check_t, _func)
        if error_list:
            print "Error Data: {0}, info: {1}".format(index_or_name, error_list)

    # fillna
    for field_item in dtypes:
        index_or_name, _t, _func, default_value = parse_field_format(field_item)
        if default_value is not None:
            data[index_or_name].fillna(default_value, inplace=True)
    #
    return data

#@add_doc(pd.read_csv)
@np.deprecate
def read_csv_old(filename, header=0, encoding='utf8', sep=';', dtypes = {},error_bad_lines=True, 
        parse_on_loading=1, check_after_load=1, filter_names=0, 
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
    filter_names: int, bool
        =1, just use columns with names listed in dtyps; =0, load all, with others be unicode type
    header: int
        set header row index, see pandas.read_csv
    encoding: string. like 'gb2312'/'utf-16' for chinese, 
        character encoding, chinese character in csv file from excel usually is 'gb2312'
        pandas raise errors when encoding is not right, and for chinese and korean,
            'utf-16' is better for that
    sep: string
    dtype: list or dict, also see: pandas.read_csv
        for Datetime field, there are two ways to decide the datetime field:
            1, type: np.datetime64, and use parse_dates (code inline)
            2, type: pd.Timestamp, and use pd.to_datetime
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
    4, encoding dismatching could cause many unexpected problems. So correct encoding data file should be firstly considerated!!

    Also see 
    --------
    http://pandas.pydata.org/pandas-docs/stable
    or 
    help(pandas.DataFrame.read_csv)
    '''
    # read data
    parsed_dtypes = [parse_field_format(field) for field in dtypes]
    #pdb.set_trace()
    dtype, parse_dates, converters, default_value_dict, field_names = parse_dtypes(parsed_dtypes)
    names = field_names if filter_names else None
    if parse_on_loading == 1:
        data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep, 
            dtype=dtype, parse_dates=parse_dates, converters = None,
            error_bad_lines=error_bad_lines, usecols=names, **kargs)
        for name, parser in converters.iteritems():
            data[name] = parser(data[name])
    else:
        data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep,
            error_bad_lines=error_bad_lines, usecols=names, **kargs)
     #pdb.set_trace()
    # check data
    if check_after_load:
        for index_or_name, _t, _func, default_value in dtypes:
            check_t = CHECK_T.get(_t, _t)
            ser, error_list = check_ser_type(data[index_or_name], check_t, _func)
        if error_list:
            print "Error Data: {0}, info: {1}".format(index_or_name, error_list)
    # fillna
    for index_or_name, default_val in default_value_dict.iteritems():
        data[index_or_name].fillna(default_val, inplace=True)
    #
    return data

def read_csv(filename, dtypes=[], sep=';', error_bad_lines=True, filter_names=True, 
        header=0, encoding='utf8', force_datetime_transform=True, fillna=True, **kargs):
    '''read csv just for detecting data errors

    first load the data with unicode to memory, then use array-level method to transform it
    if data errors happened, program will show out relevent info.
    then na_values could be used to let these wrong values to be NaN.

    Parameters
    ----------
    filename: string
    dtypes: list, dict
        define the relavant information of column 
    force_datetime_transform: bool
        used as `coerce` argument in pd.to_datetime()
    filter_names: bool
        indicate weather to just load columns define in types or not
    fillna: bool, default is True
        fill colomn with specified default value in dtypes
        if error happens, columns will not fill NaN.
    other parameters: plz see pandas.read_csv

    Returns
    -------
    data: pandas.DataFrame

    Examples
    --------
    # for data:
    id;name;amount;number;dtime
    1;雨伞;10.5;5;2011/1/1 6:05
    2;帽子;;;2012/2/3 1:20
    3;书籍;aaa;20;2012/3/11 1:20
    4;背包;30;a;2012/3/11 1:20
    5;HUADUO;30;70.9;Jan 1, 2014
    6;台灯;100;20;0

    # define relavant variables
    filename = 'mock.csv'
    # defile dtypes
    dtypes = [
        # (field_name/field_index, type, func, default_value) 
        ('id', np.int32, None,  ''),
        ('name', unicode, None, ''),  
        ('amount', np.float32, None, 0.0),
        ('number', np.int32, None, 0.0),
        ('dtime', np.datetime64, None, None)
    ]
    data = read_csv(filename, dtypes=dtypes, sep=';')
    # could see error information on console
    > check [amount]..
        [Warn] use element-level transform ..
            *Error: Index[2], Item[aaa], To Type[<type 'numpy.float32'>]
    > check [number]..
         [Warn] use element-level transform ..
            *Error: Index[1], Item[nan], To Type[<type 'numpy.int32'>]
            *Error: Index[3], Item[a], To Type[<type 'numpy.int32'>]
            *Error: Index[4], Item[70.9], To Type[<type 'numpy.int32'>]

    Notes
    -----
    field type limited to:
        unicode, str
        np.datetime64
        np.float32, np.float64
        np.int32, np.int64  # be with caution with int

    Also See
    --------
    pandas.read_csv

    '''
    parsed_dtypes = [parse_field_format(field) for field in dtypes]
    dtype, parse_dates, converters, default_value_dict, field_names = parse_dtypes(parsed_dtypes)

    names = field_names if filter_names else None
    data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep, 
            dtype='unicode', error_bad_lines=error_bad_lines, usecols=names, **kargs)

    ok_flag = 1
    for (name, field_type, field_parser, default) in parsed_dtypes:
        print("> check [{}]..".format(name.encode('utf8')))
        # np.datetime64  <-> np.dtype("<M8[ns]")
        if field_type == np.datetime64:
            field_type = np.dtype('<M8[ns]')
            new_col = pd.to_datetime(data[name], coerce=force_datetime_transform)
        # unicode/str <-> np.dtype('O')
        elif field_type in [unicode, str]:
            field_type = np.dtype('O')
            new_col = data[name]
        #
        else:
            new_col = data[name].astype(field_type, raise_on_error=False)

        if new_col.dtype == field_type: 
            data[name] = new_col
            continue
        else:
            print(" [Warn] use element-level transform ..")
            col = data[name]
            for index, item in enumerate(col):
                try:
                    col[index] = field_type(item)
                    ok_flag = 0
                except:
                    print("  *Error: Index[{}], Item[{}], To Type[{}]".format(
                        index, item, field_type))
    if fillna and ok_flag:
        for index_or_name, default_val in default_value_dict.iteritems():
            data[index_or_name].fillna(default_val, inplace=True)
    return data

#@add_doc(pd.read_table)
def read_table(filename, sep='\t', header=0, encoding='utf-8', filter_names=True, **kargs):
    ''' read txt table file by pd.read_table

    Also see
    --------
    read_csv(), the only difference with read_csv() is sep, that's why new version 
    pandas hasn't list this function
    '''
    return read_csv(filename, sep=sep, header=header, encoding=encoding, **kargs)






