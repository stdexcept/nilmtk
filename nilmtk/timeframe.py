from __future__ import print_function, division
import pandas as pd

class EmptyIntersectError(Exception):
    pass

class TimeFrame(object):
    """A TimeFrame is a single time span or period,
    e.g. from "2013" to "2014".

    Attributes
    ----------
    _start : pd.Timestamp or None
        if None then behave as if start is infinitely far into the past
    _end : pd.Timestamp or None
        if None then behave as if end is infinitely far into the future
    enabled : boolean
        If False then behave as if both _end and _start are None
    """

    def __init__(self, start=None, end=None):
        self.enabled = True
        self._start = None
        self._end = None
        self.start = start
        self.end = end

    @property
    def start(self):
        if self.enabled:
            return self._start

    @property
    def end(self):
        if self.enabled:
            return self._end
          
    @start.setter
    def start(self, new_start):
        if new_start is None:
            self._start = None
            return
        new_start = pd.Timestamp(new_start)
        if self.end and new_start > self.end:
            raise ValueError("start date must be before end date")
        else:
            self._start = new_start

    @end.setter
    def end(self, new_end):
        if new_end is None:
            self._end = None
            return
        new_end = pd.Timestamp(new_end)
        if self.start and new_end < self.start:
            raise ValueError("end date must be after start date")
        else:
            self._end = new_end

    @property
    def timedelta(self):
        if self.end and self.start:
            return self.end - self.start

    def intersect(self, other):
        """Returns a new TimeFrame of the intersection between
        this TimeFrame and `other` TimeFrame."""
        assert isinstance(other, TimeFrame)

        if other.start is None:
            start = self.start
        elif self.start is None:
            start = other.start
        else:
            start = max(self.start, other.start)
        
        if other.end is None:
            end = self.end
        elif self.end is None:
            end = other.end
        else:
            end = min(self.end, other.end)

        if (start is not None) and (end is not None):
            if start > end:
                raise EmptyIntersectError()
        
        return TimeFrame(start, end)

    @property
    def query_terms(self):
        terms = []
        if self.start is not None:
            terms.append("index>=timeframe.start")
        if self.end is not None:
            terms.append("index<timeframe.end")
        return terms

    def clear(self):
        self.start = None
        self.end = None

    def __nonzero__(self):
        return (self.start is not None) or (self.end is not None)

    def __repr__(self):
        return "TimeFrame(start={}, end={})".format(self.start, self.end)

    def __eq__(self, other):
        return (other.start == self.start) and (other.end == self.end)
