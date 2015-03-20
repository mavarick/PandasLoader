PandasLoader
============

Example
--------------------
See pd_io.read_csv function for details

NOTES
-----
  1. np.datetime64. if none, it's NaT, if 0, means '1970-01-01 00:00:00'
  2. if nrows are set, pd.read_csv just read certain rows, which could save a lot of time
  3. use iconv to convert the file to utf8 before loading the data
  4. always use array methods to transform data, not element-level methods

Control Processing
------------------
compared to last commit version, this one is more simple and robust, the processing flow is below:
  1. read all data as type unicode/None.
  2. transform column defined in dtypes to wanted type, by array-level method
  3. show wrong data on console
  4. fill NaN in specified column with default value defined in dtypes

Checking Processing
-------------------
Checking processing is companied with transforming and recording. if error happened, error_list will record the first error happened in parsing, for pandas will not locate the error when use pd.read_csv. <br>
The Checking processing is:
  1. use ser.astype(new_type). One of the most efficient way to convert to new type
  2. use new_ser = type(ser).  Matched effiecient way to ser.astype(new_type)
  3. use iteration convertion on each element. which is most inefficient, but error could be located
see code for details. <br>

p.s. convertion test by timeit <br>
data is 10000-length string series
```
|*method*|*testing result*|
| ser.astype(np.float32) | 1000 loops, best of 3: 281 µs per loop |
| np.float32(ser) | 1000 loops, best of 3: 248 µs per loop |
| [float(x) for x in ser] | 100 loops, best of 3: 1.77 ms per loop |
| map(lambda x:np.float32(x), ser) | 100 loops, best of 3: 9.75 ms per loop |  
```

Problems
--------
1, nan with type: type<'float'>, and if ser =Series[nan, NaN], you should use ser.fillna(val)
twice to fill the na value totally!

TODO
----
  1. use index number in dtypes, in case of non-english name, which could be annoying




