# PandasLoader

Simple Usage Example
=================
dtypes is an easy way to define field type of DataFrame.
      dtypes = [
          # (field_name/field_index, type, default_value)
          # if default_value is None, result will be NaN in DataFrame
          (‘id', np.int32, 0),
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
