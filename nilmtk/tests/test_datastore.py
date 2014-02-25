#!/usr/bin/python
from __future__ import print_function, division
import unittest
from os.path import join
import pandas as pd
from datetime import timedelta
from testingtools import data_dir
from nilmtk.datastore import HDFDataStore
from nilmtk import TimeFrame

class TestHDFDataStore(unittest.TestCase):
    START_DATE = pd.Timestamp('2012-01-01 00:00:00', tz=None)
    NROWS = 1E4
    END_DATE = START_DATE + timedelta(seconds=NROWS-1)
    TIMEFRAME = TimeFrame(START_DATE, END_DATE)

    @classmethod
    def setUpClass(cls):
        filename = join(data_dir(), 'random.h5')
        cls.datastore = HDFDataStore(filename)
        cls.keys = ['/building1/utility/electric/meter{:d}'.format(i) 
                    for i in range(1,6)]

    @classmethod
    def tearDownClass(cls):
        cls.datastore.close()

    def test_keys(self):
        self.assertEqual(self.datastore.keys(), self.keys)

    def test_column_names(self):
        for key in self.keys:
            self.assertEqual(self.datastore.column_names(key), 
                             [('power', 'active'), 
                              ('power', 'reactive'), 
                              ('voltage', '')])

    def test_timeframe(self):
        self.datastore.window.clear()
        for key in self.keys:
            self.assertEqual(self.datastore.timeframe(key), self.TIMEFRAME)

        self._apply_mask()
        for key in self.keys:
            self.datastore.window.enabled = False
            self.assertEqual(self.datastore.timeframe(key), self.TIMEFRAME)
            self.datastore.window.enabled = True
            self.assertEqual(self.datastore.timeframe(key), self.datastore.window)

    def test_n_rows(self):
        self._apply_mask()
        for key in self.keys:
            self.datastore.window.enabled = True
            self.assertEqual(self.datastore.nrows(key), 10*60)
            self.datastore.window.enabled = False
            self.assertEqual(self.datastore.nrows(key), self.NROWS)

    def test_estimate_memory_requirement(self):
        self._apply_mask()
        for key in self.keys:
            self.datastore.window.enabled = True
            mem = self.datastore.estimate_memory_requirement(key)
            self.assertEqual(mem, 12000)
            self.datastore.window.enabled = False
            mem = self.datastore.estimate_memory_requirement(key)
            self.assertEqual(mem, 200000)

    def test_load(self):
        timeframe = TimeFrame('2012-01-01 00:00:00', '2012-01-01 00:00:05')
        self.datastore.window.clear()
        df = self.datastore.load(key=self.keys[0], 
                                 cols=[('power', 'active')],
                                 window=timeframe)
        self.assertEqual(df.index[0], timeframe.start)
        self.assertEqual(df.index[-1], timeframe.end - timedelta(seconds=1))

    def test_generator(self):
        self.datastore.window.clear()
        chunks = self.datastore.generator(self.keys[0])
        i = 0
        for chunk in chunks:
            i += 1
            self.assertEqual(chunk.index[0], self.TIMEFRAME.start)
            self.assertEqual(chunk.index[-1], self.TIMEFRAME.end-timedelta(seconds=1))
            self.assertEqual(len(chunk), self.NROWS-1)
        self.assertEqual(i, 1)

        timeframes = [TimeFrame('2012-01-01 00:00:00', '2012-01-01 00:00:05'),
                      TimeFrame('2012-01-01 00:10:00', '2012-01-01 00:10:05')]
        chunks = self.datastore.generator(self.keys[0], periods=timeframes)
        i = 0
        for chunk in chunks:
            self.assertEqual(chunk.index[0], timeframes[i].start)
            self.assertEqual(chunk.index[-1], timeframes[i].end-timedelta(seconds=1))
            self.assertEqual(len(chunk), 5)
            i += 1
        self.assertEqual(i, 2)

        # Check when we have a narrow mask
        self.datastore.window = TimeFrame('2012-01-01 00:10:02', '2012-01-01 00:10:10')
        chunks = self.datastore.generator(self.keys[0], periods=timeframes)
        i = 0
        for chunk in chunks:
            self.assertEqual(chunk.index[0], pd.Timestamp('2012-01-01 00:10:02'))
            self.assertEqual(chunk.index[-1], pd.Timestamp('2012-01-01 00:10:04'))
            self.assertEqual(len(chunk), 3)
            i += 1
        self.assertEqual(i, 1)


    #--------- helper functions ---------------------#

    def _apply_mask(self):
        self.datastore.window = TimeFrame('2012-01-01 00:10:00',
                                        '2012-01-01 00:20:00')

    
if __name__ == '__main__':
    unittest.main()
