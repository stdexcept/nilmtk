#!/usr/bin/python
from __future__ import print_function, division
import unittest
import pandas as pd
from nilmtk.timeframe import TimeFrame, EmptyIntersectError

class TestTimeFrame(unittest.TestCase):
    def test_date_setting(self):
        TimeFrame()
        TimeFrame("2012-01-01", "2013-01-01")
        TimeFrame("2012-01-01", "2012-01-01")
        TimeFrame(start="2011-01-01")
        TimeFrame(end="2011-01-01")
        with self.assertRaises(ValueError):
            TimeFrame("2012-01-01", "2011-01-01")
        tf = TimeFrame()
        tf.end = "2011-01-01"
        tf.start = "2010-01-01"
        with self.assertRaises(ValueError):
            tf.start = "2012-01-01"

    def test_time_delta(self):
        tf = TimeFrame("2012-01-01 00:00:00", "2013-01-01 00:00:00")        
        self.assertEqual(tf.timedelta.total_seconds(), 60*60*24*366)

    def test_intersect(self):
        tf = TimeFrame("2012-01-01 00:00:00", "2013-01-01 00:00:00")

        new_tf = tf.intersect(tf)
        self.assertEqual(tf, new_tf)

        new_tf = tf.intersect(TimeFrame())
        self.assertEqual(tf, new_tf)

        new_tf = tf.intersect(TimeFrame(start="1990-01-01"))
        self.assertEqual(tf, new_tf)        

        new_tf = tf.intersect(TimeFrame(end="2100-01-01"))
        self.assertEqual(tf, new_tf)        

        small_tf = TimeFrame("2012-01-05 00:00:00", "2012-01-06 00:00:00")
        new_tf = tf.intersect(small_tf)
        self.assertEqual(small_tf, new_tf)

        large_tf = TimeFrame("2010-01-01 00:00:00", "2014-01-01 00:00:00")
        new_tf = tf.intersect(large_tf)
        self.assertEqual(tf, new_tf)

        disjoint = TimeFrame("2015-01-01", "2016-01-01")
        with self.assertRaises(EmptyIntersectError):
            new_tf = tf.intersect(disjoint)

        disjoint = TimeFrame("2015-01-01", "2016-01-01")
        tf.enabled = False
        new_tf = tf.intersect(disjoint)
        self.assertEqual(new_tf, disjoint)
        tf.enabled = True

        # crop into the start of tf
        new_start = "2012-01-05 04:05:06"
        new_tf = tf.intersect(TimeFrame(start=new_start, end="2014-01-01"))
        self.assertEqual(new_tf, TimeFrame(start=new_start, end=tf.end))

        # crop into the end of tf
        new_end = "2012-01-07 04:05:06"
        new_tf = tf.intersect(TimeFrame(start="2011-01-01", end=new_end))
        self.assertEqual(new_tf, TimeFrame(start=tf.start, end=new_end))
        

if __name__ == '__main__':
    unittest.main()
