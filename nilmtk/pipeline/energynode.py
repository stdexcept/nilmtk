from __future__ import print_function, division
from node import Node
from energyresults import EnergyResults
import numpy as np
from nilmtk.utils import timedelta64_to_secs
from nilmtk.consts import JOULES_PER_KWH, POWER_NAMES
from nilmtk import TimeFrame
from nilmtk.pipeline import Contract

def _energy_per_power_series(series):
    timedelta = np.diff(series.index.values)
    timedelta_secs = timedelta64_to_secs(timedelta)
    joules = (timedelta_secs * series.values[:-1]).sum()
    return joules / JOULES_PER_KWH

class EnergyNode(Node):

    preconditions = Contract(gaps_bookended_with_zeros=True)
    postconditions =  Contract(energy_computed=True)

    def __init__(self, name='energy'):
        super(EnergyNode, self).__init__(name)

    def process(self, df):
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
