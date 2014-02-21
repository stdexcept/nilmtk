"""
Tools to help with testing.
"""

from __future__ import print_function, division
import os, inspect

def data_dir():
    # Taken from http://stackoverflow.com/a/6098238/732596
    current_file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
    data_dir = os.path.join(current_file_path, '..', '..', 'data')
    data_dir = os.path.abspath(data_dir)
    assert os.path.isdir(data_dir), data_dir + " does not exist."
    return data_dir

