import abc
import pandas as pd

class Results(object):
    """Metadata results from each node need to be assigned to a specific
    class so we know how to combine results from multiple chunks.  For
    example, Energy can be simply summed; while dropout rate should be
    averaged, and gaps need to be merged across chunk boundaries.  Results
    objects contain a DataFrame, the index of which is the start timestamp for
    which the results are valid; the first column ('end') is the end
    timestamp for which the results are valid.  Other columns are accumaltors for the results.

    Attributes
    ----------
    _data : DataFrame
        Index is period start.  
        Columns are: end_date and any columns for internal storage of stats.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._data = pd.DataFrame(columns=['end'])

    @abc.abstractproperty
    def combined(self):
        """Return all results from each chunk combined.
        Either return single float for all periods or a dict where necessary, 
        e.g. if calculating Energy for a meter which records both apparent power and
        active power then we've have energyresults.combined['active']
        """
        pass
        
    @abc.abstractproperty
    def per_period(self):
        """return a DataFrame.  Index is period start.  Columns are: end_date and <stat name>
        """
        pass

    @abc.abstractmethod
    def update(self, new_result):
        """Update with new results"""
        pass
