from results import Results
import pandas as pd
import numpy as np
import copy
from collections import OrderedDict
from nilmtk import TimeFrame

class EnergyResults(Results):
    """
    Attributes
    ----------
    _data : pd.DataFrame
        index is start date
        `end` is end date
        `active` is (optional) energy in kWh
        `reactive` is (optional) energy in kVARh
        `apparent` is (optional) energy in kVAh
    """
    
    @property
    def combined(self):
        """Return all results from each chunk combined.
        Either return single float for all periods or a dict where necessary, 
        e.g. if calculating Energy for a meter which records both apparent power and
        active power then we've have energyresults.combined['active']
        """
        cols = set(self._data.columns)
        cols.remove('end')
        cols = list(cols)
        return self._data[cols].sum()

    @property
    def per_period(self):
        """return a DataFrame.  Index is period start.  
        Columns are: end and <stat name>
        """
        return copy.deepcopy(self._data)

    def append(self, timeframe, **args):
        """Append a single result."""
        allowed_columns = ['active', 'apparent', 'reactive']
        if set(args.keys()) - set(allowed_columns):
            raise KeyError('kwargs must be a combination of '+
                           str(allowed_columns))
        data = pd.DataFrame(index=[timeframe.start])
        data['end'] = timeframe.end
        for key, val in args.iteritems():
            data[key] = val
        new_result = EnergyResults()
        new_result._data = data
        self.update(new_result)

    def update(self, new_result):
        """Update with new result."""
        if not isinstance(new_result, EnergyResults):
            raise TypeError('new_results must be of type EnergyResults')

        if 'end' in self._data:
            if np.intersect1d(self._data['end'], new_result._data['end']):
                raise ValueError("Overlap between end dates")

        # check that there is no overlap
        for index, series in self._data.iterrows():
            tf = TimeFrame(index, series['end'])
            for new_index, new_series in new_result._data.iterrows():
                new_tf = TimeFrame(new_index, new_series['end'])
                intersect = tf.intersect(new_tf)
                if not intersect.empty:
                    raise ValueError("Periods overlap" + str(intersect))

        # append the data and verify there are no duplicate indicies
        self._data = self._data.append(new_result._data, verify_integrity=True)
        self._data.sort_index(inplace=True)
        
        # make sure 'end' is the first column
        cols = list(self._data.columns)
        cols.remove('end')
        cols.insert(0, 'end')
        self._data = self._data.reindex_axis(cols, axis=1, copy=False)
