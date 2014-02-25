from __future__ import print_function, division
from node import Node
from energyresults import EnergyResults
import numpy as np
from nilmtk.utils import timedelta64_to_secs
from nilmtk.consts import JOULES_PER_KWH, POWER_NAMES
from nilmtk import TimeFrame

def _energy_per_power_series(series):
    timedelta = np.diff(series.index.values)
    timedelta_secs = timedelta64_to_secs(timedelta)
    joules = (timedelta_secs * series.values[:-1]).sum()
    return joules / JOULES_PER_KWH

class EnergyNode(Node):

    # postconditions =  {} # TODO

    def __init__(self, name='energy'):
        super(EnergyNode, self).__init__(name)

    def process(self, df):
        # check_preconditions again??? (in case this node is not run in
        # the context of a Pipeline?)
        # do stuff to df
        energy = {}
        for power_name in POWER_NAMES:
            energy_measurement = ('energy', power_name)
            power_measurement = ('power', power_name)
            if energy_measurement in df.columns:
                energy[power_name] = df[energy_measurement].sum()
            elif power_measurement in df.columns:
                energy[power_name] = _energy_per_power_series(
                    df[power_measurement])

        results = df.__dict__.get('results', {})
        energy_results = EnergyResults()
        energy_results.append(TimeFrame(df.index[0], df.index[-1]),
                              **energy)
        results[self.name] = energy_results
        df.results = results
        return df

    def check_preconditions(conditions):
        """ Static method

        Parameters
        ----------
        conditions : dict
        
        Returns
        -------
        boolean
        
        Description
        -----------
        
        Requirements can be of the form:
    
        "node X needs (power.apparent or power.active) (but not
        power.reactive) and voltage is useful but not essential"
    
        or
    
        "node Y needs everything available from disk (to save to a copy to
        disk)"
    
        or
    
        "ComputeEnergy node needs gaps to be bookended with zeros" (if
        none of the previous nodes provide this service then check
        source.metadata to see if zeros have already been inserted; if the
        haven't then raise an error to tell the user to add a
        BookendGapsWithZeros node.)
        """
        # TODO: see if there are any unsatisfied preconditions
        # if there are then raise an UnsatisfiedPreconditionsError
        # giving the exact precondition that failed, why it failed
        # which node is complaining, and suggestions for how to fix it
        pass        

