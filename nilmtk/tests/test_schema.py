#!/usr/bin/python
from __future__ import print_function, division
import unittest
from nilmtk import Schema

class TestSchema(unittest.TestCase):

    def test_constructor(self):
        Schema(a=bool, b=str, c=int, d=tuple)
        with self.assertRaises(TypeError):
            Schema(a=1)
        with self.assertRaises(TypeError):
            Schema(a='a')            
        with self.assertRaises(TypeError):
            Schema(b=('a', 2))
        with self.assertRaises(TypeError):
            Schema(a=bool, b=str, c=int, d=tuple, e=1)
        with self.assertRaises(TypeError):
            Schema(a=bool, b=2, c=int, d=tuple)

    def test_validate(self):
        schema = Schema(name=str, exists=bool, geo=tuple)
        schema.validate({'name':'George', 'exists':True, 'geo':(12,34)})
        with self.assertRaises(TypeError):        
            schema.validate({'name':True, 'exists':True, 'geo':(12,34)})
        with self.assertRaises(TypeError):        
            schema.validate({'name':'George', 'exists':'gah', 'geo':(12,34)})
        with self.assertRaises(TypeError):        
            schema.validate({'name':'George', 'exists':True, 'geo':12})
        with self.assertRaises(ValueError):
            schema.validate({'gah':'George', 'exists':True, 'geo':(12,34)})

if __name__ == '__main__':
    unittest.main()
