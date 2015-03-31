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
        :(name, ) : be left to pandas to parse type
        :(name, type, ): with parse_func = type, and default is None
        :(name, type, parser, ): with default is None
        or of type dict:
        {"name": name, 'type'=type, 'parser': parser, 'default':default_val}
        :{"name": name}: be left to pandas to parse type automatically
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
        field_type = field_item.get('type', None)
        field_parser = field_item.get("parser", DEFAULT_PARSER)
        default = field_item.get("default", None)
        if field_type is None:
            print("Warn: Col[{}] is left to pandas to parse the type, ".format(name) +
                "cause no type is specified")
            return None
    elif type(field_item) in [list, tuple]:
        args_number = len(field_item)
        if args_number == 1:
            print("Warn: Col[{}] is left to pandas to parse the type, ".format(name) +
                "cause no type is specified")
            return None
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

def parse_field_format_from_dict(dtypes):
    '''parse field type from dict,

    more easier way to use read_csv, especially with very many columns

    Parameters
    ----------
    dtypes: dict, with format: 
        {
        (np.float32, default_val): ['col1', 'col2', ...],
        (np.float32, default_val2): ['col11', 'col22', ...]
        (np.datetime64, default_val3): ['col3', 'col4', ...]
        }

    Returns
    -------
    [(name, type, parser, default)]
    '''
    parsed_dtypes = []
    for (_t, default_val), fields in dtypes.iteritems():
        for field in fields:
            parsed_dtypes.append(parse_field_format(
                    {'name': field, 'type': _t, 'default': default_val}
                ))
    return parsed_dtypes

def parse_field_format_from_list(dtypes):
    '''parse defined field format

    Parameters
    ----------
    dtypes: list of tuple or dict,
        tuple: (name, type, parser, default)
        dict:  {"name": name, 'type'=type, 'parser': parser, 'default':default_val}
    '''
    formats = []
    for field in dtypes:
        f = parse_field_format(field)
        if f: 
            formats.append(f)
    return formats

def parse_fields(dtypes):
    return {
        dict: parse_field_format_from_dict, 
        list:parse_field_format_from_list
        }[type(dtypes)](dtypes)

#@add_doc(pd.read_csv)
def read_excel(filename, sheet_name=0, header=0, dtypes=[], **kargs):
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

def read_csv(filename, dtypes=[], sep=';', error_bad_lines=True, filter_names=False, 
        header=0, encoding='utf8', force_datetime_transform=True, fillna=True, 
        **kargs):
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
        ('name', )  # will left to pandas to parse type automatically
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
    parsed_dtypes = parse_fields(dtypes)

    dtype, parse_dates, converters, default_value_dict, field_names = parse_dtypes(parsed_dtypes)

    names = field_names if filter_names else None
    data = pd.read_csv(filename, header=header, encoding=encoding, sep=sep, 
            dtype=None, error_bad_lines=error_bad_lines, usecols=names,
             **kargs)

    ok_flag = 1
    for (name, field_type, field_parser, default) in parsed_dtypes:
        print("> check [{}]..".format(name.encode('utf8')))
        # np.datetime64  <-> np.dtype("<M8[ns]")
        if field_type == np.datetime64:
            field_type = np.dtype('<M8[ns]')
            new_col = pd.to_datetime(data[name], coerce=force_datetime_transform)
        # unicode/str <-> np.dtype('O')
        elif field_type in [unicode, str, np.str, np.unicode, np.str_]:
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
                    col[index] = field_parser(item)
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


def read_csv_simple(filename, dtypes=[], filter_names=False, sep=';', header=0, encoding='utf8',
        debug_transform=True, force_datetime_transform=True, **kargs):
    '''read csv file for simplicity of `read_csv`

    Parameters
    ----------
    filename: string
    dtypes: list of tuples, default is []
        define the types of columns
    filter_names: boolean, default is False
        weather only columns in dtypes are read or total columns
    sep: character, default is ';'
        sperator between columns
    header: int,  default is 0
        table header
    encoding: string, default is utf8
    debug_transform: boolean, default is True
        if True, then use element transformation function to transform the data, or just give one warn tip
    force_datetime_transform: boolean, default is True
        coerce value when using to_datetime function, when transform value to datetime

    Dtypes:
    -------
    (name|name_list, )  # just for knowing it
    (name|name_list, type, default)  # 
        type options:
        1, np.float64, np.float, np.float32
        2, np.int64, np.int32, np.int
        3, np.datetime64
        4, np.str, np.unicode, np.str_, str, unicode
    (name, type, parser, default) # feel cumsumber

    Examples
    --------


    Notes
    -----
    Some Annoying problems Occurred, when you want one column be int but with NaN value
    at this time, col.dtype will never be np.int(32, 64).
    so:
        1, use float instead of int;
        2, use default value as possible as you can.

    Returns
    -------
    data: pandas.DataFrame
        with specified columns and types or not

    '''
    # parse the dtypes
    names = []
    name_parsers = []
    for d in dtypes:
        len_d = len(d)

        if len_d == 1:
            if type(d[0]) in [list, set, tuple]:
                names.extend(d[0])
            else:
                names.append(d[0])
        if len_d == 3:
            names, _type, default = d 
            names = names if type(names) in [list, set, tuple] else [names]
            for name in names:
                name_parsers.append((name, _type, default))

    # read the files
    use_col_names = names if filter_names else None
    data = pd.read_csv(filename, dtype=None, sep=sep, header=header, encoding=encoding, 
        usecols=use_col_names, **kargs)

    type_dict = {
            "float": np.float,
            "floa32": np.float32,
            "float64": np.float64,
            float: np.float,

            "int": np.int,
            "int32": np.int32,
            "int64": np.int64,
            int: np.int,

            "datetime": pd.Timestamp,
            "datetime64": pd.Timestamp,

            "str": np.str,
            "unicode": np.unicode,
            str: np.str,
            unicode: np.unicode
    }
    float_type_list = [np.float, np.float32, np.float64]
    int_type_list = [np.int, np.int32, np.int64]
    datetime_type_list = [np.datetime64, np.dtype('<M8[ns]'), pd.Timestamp]
    str_type_list = [np.str, np.unicode]

    # check the column types
    for item in name_parsers:
        name, _type, default = item  
        # till here, the data should be of one type, e.x. np.float64, or mixed of two types,
        # e.x. [np.str, np.nan]
        _type = type_dict.get(_type, _type)
        if default is None:
            print("Warn: default value [{}] in col[{}] is transformed to [{}]".format(
                default, name, np.nan))
            default = np.nan

        # fillna
        data[name].fillna(default, inplace=True)

        # transform data to specfied type
        # float-like type
        if _type in float_type_list:
            if data[name].dtype not in float_type_list: 
                # some special data occur! 
                data[name] = data[name].astype(_type, raise_on_error=False)
            if data[name].dtype not in float_type_list:
                print(">> col[{}] can not be astyped to {}".format(name, _type))
                if debug_transform:
                    col = data[name]
                    for index, value in enumerate(col):
                        try:
                            col[index] = _type(value)
                        except:
                            print("force>> value[{}] in col[{}] can not be transformed to {}".format(
                                col[index], name, _type) + " , and is forced to default[{}]".format(default))
                            col[index] = default
                    data[name] = col.astype(_type)

        # int-like type
        if _type in int_type_list:
            if data[name].dtype not in int_type_list:
                data[name] = data[name].astype(_type, raise_on_error=False)
            if data[name].dtype not in int_type_list:
                print(">> col[{}] can not be astyped to {}".format(name, _type))
                if debug_transform:
                    col = data[name]
                    for index, value in enumerate(col):
                        try:
                            col[index] = _type(value)
                        except:
                            print("force>> value[{}] in col[{}] can not be transformed to {}".format(
                                col[index], name, _type) + " , and is forced to default[{}]".format(default))
                            col[index] = default
                    data[name] = col.astype(_type)
        # datetime-like type
        if _type in datetime_type_list:
            data[name] = pd.to_datetime(data[name], coerce=force_datetime_transform)
            data[name].fillna(default, inplace=True)
            if data[name].dtype not in datetime_type_list:
                print(">> col[{}] can not transormed to datetime type: {},".format(name, _type) + 
                    " or the default value is not valid")
        # str-like type
        if _type in str_type_list:
            data[name] = data[name].astype(_type, raise_on_error=False)

    return data

