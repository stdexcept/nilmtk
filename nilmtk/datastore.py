from __future__ import print_function, division
import pandas as pd

MAX_MEM_ALLOWANCE_IN_BYTES = 1E9

class DataStore(object):
    """
    Provides a common interface to all physical data stores.  
    Supports hierarchical stores.
    
    The DataStore class lives in the bottom layer of NILMTK.  It loads
    a single chunk at a time from physical location and returns a
    DataFrame.

    * Deals with: retrieving data from disk / network / direct from a meter
    * Optimised for: handling large amounts of data
    * Services it provides: delivering a pd.DataFrame of data given a
      specific time span and columns
    * Totally agnostic about what the data 'means'. It could be voltage,
      current, temperature, PIR readings etc.
    * subclasses for NILMTK HDF5, NILMTK CSV, Xively, REDD, iAWE,
      UKPD, etc; MetOffice XLS data, Current Cost meters etc.  
    * One DataStore per HDF5 file or folder or CSV files or Xively
      feed etc 
    * always use JSON for metadata

    Only opens the underlying data source when absolutely necessary 
    (by minimising the time the data source is open, we can minimise
    the chance of data being corrupted if another process changes it).
    """
    pass


class HDFDataStore(DataStore):
    def __init__(self, filename, start_date=None, end_date=None):
        """
        Parameters
        ----------
        filename : string
        start_date, end_date : pd.Timestamp or string, optional
            Defines a "region of interest", 
            i.e. crops the data non-destructively.
        """
        self.store = pd.HDFStore(filename)
        self.store.close()
        self.start_date = pd.Timestamp(start_date) if start_date else None
        self.end_date = pd.Timestamp(end_date) if end_date else None

    def load(self, key, cols=None, start_date=None, end_date=None):
        """
        Parameters
        ----------
        key : string, the location of a table within the DataStore.
            The hierarchical structure of key is standardised across NILMTK
            e.g. 'building1/utility/electric/meter4'. Or, if the physical
            store only represents, say, a single house then the path is
            truncated to 'utility/electric/meter4'.  
        cols : list or 'index', optional
            e.g. [('power', 'active'), ('power', 'reactive'), ('voltage', '')]
            if not provided then will return all columns from the table.
        start_date, end_date : string or pd.Timestamp, optional
            defines the time period to load as range (start_date, end_date]

        Returns
        ------- 
        If `cols=='index'` then returns a pd.DatetimeIndex
        else returns a pd.DataFrame

        Raises
        ------
        MemoryError if we try to load too much data.
        """
        self._check_key(key)
        start_date, end_date = self.restrict_start_and_end_dates(start_date, 
                                                                 end_date)
        
        # Create list of query terms
        terms = date_range_to_terms(start_date, end_date)
        if cols is not None:
            if not self.table_has_column_names(key, cols):
                raise KeyError('at least one of ' + str(cols) + 
                               ' is not a valid column')
            terms.append("columns==cols")
        if terms == []:
            terms = None
        
        # Check we won't use too much memory
        mem_requirement = self.estimate_memory_requirement(key, cols, 
                                                           start_date, end_date)
        if mem_requirement > MAX_MEM_ALLOWANCE_IN_BYTES:
            raise MemoryError('Requested data would use too much memory.')
        
        # Read data
        self.store.open()
        data = self.store.select(key=key, where=terms, auto_close=True)
        if cols == 'index':
            data = data.index
        return data
    
    def table_has_column_names(self, key, cols):
        """
        Parameters
        ----------
        cols : string or list of strings
        
        Returns
        -------
        boolean
        """
        self._check_key(key)
        if isinstance(cols, str):
            cols = [cols]
        query_cols = set(cols)
        table_cols = set(self.column_names(key) + ['index'])
        return query_cols.issubset(table_cols)
    
    def get_generator(self, key, periods=None, cols=None):
        """
        Parameters
        ----------
        periods : list of (start_date, end_date) tuples, optional
            e.g. [("2013-01-01", "2013-02-01"), ("2013-02-01", "2013-03-01")]
            
        """
        
        # TODO: this would be much more efficient 
        # if we first got row indicies for each period,
        # then checked each period will fit into memory,
        # and then iterated over the row indicies.      
        self._check_key(key)  
        if periods is None:
            periods = [self.date_range(key)]
        for start_date, end_date in periods:
            data = self.load(key, cols, start_date, end_date)
            if not data.empty:
                yield data
    
    def estimate_memory_requirement(self, key, cols=None, start_date=None, 
                                    end_date=None, apply_mask=True):
        """Returns estimated mem requirement in bytes."""
        BYTES_PER_ELEMENT = 4
        BYTES_PER_TIMESTAMP = 8
        self._check_key(key)
        if cols is None:
            cols = self.column_names(key)
        ncols = len(cols)
        nrows = self.nrows(key, start_date, end_date, apply_mask=apply_mask)
        est_mem_usage_for_data = nrows * ncols * BYTES_PER_ELEMENT
        est_mem_usage_for_index = nrows * BYTES_PER_TIMESTAMP
        return est_mem_usage_for_data + est_mem_usage_for_index
    
    def column_names(self, key):
        self._check_key(key)
        storer = self._get_storer(key)
        col_names = storer.non_index_axes[0][1:][0]
        self.store.close()
        return col_names
    
    def nrows(self, key, start_date=None, end_date=None, apply_mask=True):
        self._check_key(key)
        if apply_mask:
            start_date, end_date = self.restrict_start_and_end_dates(start_date, end_date)
        if start_date or end_date:
            terms = date_range_to_terms(start_date, end_date)
            if terms == []:
                terms = None
            self.store.open()
            coords = self.store.select_as_coordinates(key, terms)
            nrows_ = len(coords)
        else:
            storer = self._get_storer(key)
            nrows_ = storer.nrows
            self.store.close()
        return nrows_
    
    def restrict_start_and_end_dates(self, start_date=None, end_date=None):
        if start_date:
            start_date = pd.Timestamp(start_date)
        if end_date:
            end_date = pd.Timestamp(end_date)
            
        if all([start_date, self.start_date]) and start_date < self.start_date:
            start_date = self.start_date
        elif start_date is None:
            start_date = self.start_date
        if all([end_date, self.end_date]) and end_date > self.end_date:
            end_date = self.end_date
        elif end_date is None:
            end_date = self.end_date
        return start_date, end_date
    
    def date_range(self, key, apply_mask=True):
        """
        Returns
        -------
        (start_date, end_date)
        """
        self._check_key(key)
        self.store.open()
        start_date = self.store.select(key, [0]).index[0]
        end_date = self.store.select(key, start=-1).index[0]
        self.store.close()
        if apply_mask:
            start_date, end_date = self.restrict_start_and_end_dates(start_date,
                                                                     end_date)
        return start_date, end_date
    
    def keys(self):
        self.store.open()
        keys = self.store.keys()
        self.store.close()
        return keys

    def _get_storer(self, key):
        """Caller must close store."""
        self._check_key(key)
        self.store.open()
        storer = self.store.get_storer(key)
        assert storer is not None, "cannot get storer for key = " + key
        return storer
    
    def _check_key(self, key):
        if key not in self.keys():
            raise KeyError(key + ' not in store')


def date_range_to_terms(start_date=None, end_date=None):
    terms = []
    if start_date is not None:
        terms.append("index>=start_date")
    if end_date is not None:
        terms.append("index<end_date")
    return terms

# SIMPLE TESTS:
# ds = HDFDataStore('../data/random.h5',
#         start_date='2012-01-01 00:00:30', end_date='2012-01-01 00:00:59')
# KEY = '/building1/utility/electric/meter1'
# print('columns =', ds.column_names(KEY))
# print('date range (with region of interest applied) = \n', ds.date_range(KEY))
# print('date range (with region of interest lifted) = \n', ds.date_range(KEY, apply_mask=False))
# print('number of rows (ROI applied) =', ds.nrows(KEY))
# print('number of rows (ROI lifted) =', ds.nrows(KEY, apply_mask=False))
# print('estimated memory requirement for all data (ROI applied) = {:.1f} MBytes'
#       .format(ds.estimate_memory_requirement(KEY) / 1E6))
# print('estimated memory requirement for all data (ROI lifted)  = {:.1f} MBytes'
#       .format(ds.estimate_memory_requirement(KEY, apply_mask=False) / 1E6))
# ds.load(KEY, start_date='2012-01-01 00:00:00', 
#         end_date='2012-01-01 00:00:05', 
#         cols=[('power', 'active')])
# for chunk in ds.get_generator(KEY, [
#         ("2012-01-01 00:00:00", "2012-01-01 00:00:10"), 
#         ("2012-01-01 00:00:50", "2012-01-01 00:00:59")]):
#     print('start = ', chunk.index[0], '; end =', chunk.index[-1])
