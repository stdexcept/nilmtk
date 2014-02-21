#!/usr/bin/python
from __future__ import print_function, division
import unittest
from os.path import join
import pandas as pd
from datetime import timedelta
from testingtools import data_dir
from nilmtk.datastore import HDFDataStore

class TestHDFDataStore(unittest.TestCase):
    START_DATE = pd.Timestamp('2012-01-01 00:00:00', tz=None)
    NROWS = 1E4
    END_DATE = START_DATE + timedelta(seconds=NROWS-1)

    def setUp(self):
        filename = join(data_dir(), 'random.h5')
        self.datastore = HDFDataStore(filename)
        self.keys = ['/building1/utility/electric/meter{:d}'.format(i) 
                     for i in range(1,6)]

    def test_keys(self):
        self.assertEqual(self.datastore.keys(), self.keys)

    def test_column_names(self):
        for key in self.keys:
            self.assertEqual(self.datastore.column_names(key), 
                             [('power', 'active'), 
                              ('power', 'reactive'), 
                              ('voltage', '')])

    def test_date_range(self):
        for key in self.keys:
            self.assertEqual(self.datastore.date_range(key),
                             (self.START_DATE, self.END_DATE))

        self.datastore.start_date = pd.Timestamp('2012-01-01 00:10:00')
        self.datastore.end_date = pd.Timestamp('2012-01-01 00:20:00')

        for key in self.keys:
            self.assertEqual(self.datastore.date_range(key),
                             (self.datastore.start_date, self.datastore.end_date))
            self.assertEqual(self.datastore.date_range(key, apply_mask=False),
                             (self.START_DATE, self.END_DATE))
        
        self.datastore.start_date = None
        self.datastore.end_date = None
        for key in self.keys:
            self.assertEqual(self.datastore.date_range(key),
                             (self.START_DATE, self.END_DATE))
                                                
    def test_n_rows(self):
        for key in self.keys:        
            self.assertEqual(self.datastore.nrows(key), self.NROWS)

    
if __name__ == '__main__':
    unittest.main()
