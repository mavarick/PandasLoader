Simple Usage Example
=================
dtypes is an easy way to define field type of DataFrame.
     dtypes = [
          # (field_name/field_index, type, default_value)
          # if default_value is None, result will be NaN in DataFrame
          (‘id', np.float64, 0),
          (’name', unicode, ''), # element should have type unicode
          ('amount', to_float32, None),
          (4, np.datetime64, None)
     ]
dtypes will be classified in to dtype, converter, parse_dates in pandas read_csv arguments.
converter function should be like this:
      def to_float32(target_val, default_val):
          try:
               new_val = np.float32(target_val)
          except:
               new_val = default_val
          return new_val
then, use read_csv to load data:
      data = read_csv(filename, encoding='gb2312', dtypes=dtypes)

Control Processing
===============
use `parse_on_loading` and `check_after_load` to control the overflow!
Be aware of this:
     1. if want to use pandas datetime parse, like use `parse_dates` in pd.read_csv, parse_on_loading should be 1
     2. if want to debug the data, parse_on_loading should be 0 eapecially when data is large: data should be first in memory

Checking Processing
===============
Checking processing is companied with transforming and recording. if error happened, error_list will record the first error happened in parsing, for pandas will not locate the error when use pd.read_csv
The Checking processing is:
     1. use ser.astype(new_type). One of the most efficient way to convert to new type
     2. use new_ser = type(ser).  Matched effiecient way to ser.astype(new_type)
     3. use iteration convertion on each element. which is most inefficient, but error could be located
see code for details.
p.s. convertion test by timeit
data is 10000-length string series
|*method*|*testing result*|
| ser.astype(np.float32) | 1000 loops, best of 3: 281 µs per loop |
| np.float32(ser) | 1000 loops, best of 3: 248 µs per loop |
| [float(x) for x in ser] | 100 loops, best of 3: 1.77 ms per loop |
| map(lambda x:np.float32(x), ser) | 100 loops, best of 3: 9.75 ms per loop |


BETTER-DO
=========
  1. use np.float64 to represent int type. or NaN value will raise.
  2. 

TODO
=====
  1. use index number in dtypes, in case of non-english name, which could be annoying




