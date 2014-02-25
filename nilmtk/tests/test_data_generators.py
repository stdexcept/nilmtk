from __future__ import print_function, division
import pandas as pd
from datetime import timedelta

def power_data():
    """
    Returns a DataFrame with columns:
    (power, active)  (power, reactive)  (power, apparent)  (energy, active)
    """
    MAX_SAMPLE_PERIOD = 15
    JOULES_PER_KWH = 3600000

    data = [0,  0,  0, 100, 100, 100, 150, 150, 200,   0,   0, 100, 5000,    0]
    secs = [0, 10, 20,  30, 200, 210, 220, 230, 240, 249, 260, 270,  290, 1000]

    data = np.array(data, dtype=np.float32)
    active = data
    reactive = data * 0.9
    apparent = data * 1.1
    
    index = [pd.Timestamp('2010-01-01') + timedelta(seconds=sec) for sec in secs]

    df = pd.DataFrame(np.array([active, reactive, apparent]).transpose(),
                      index=index, dtype=np.float32, 
                      columns=[('power', 'active'), 
                               ('power', 'reactive'), 
                               ('power', 'apparent')])

    # calculate energy
    # this is not cumulative energy
    timedelta_secs = np.diff(secs).clip(0, MAX_SAMPLE_PERIOD).astype(np.float32)
    print(timedelta_secs.dtype)
    joules = timedelta_secs * df[('power', 'active')].values[:-1]
    joules = np.concatenate([joules, [0]])
    df[('energy', 'active')] = joules / JOULES_PER_KWH

    return df

