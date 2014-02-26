#!/usr/bin/python
from __future__ import print_function, division
import unittest
from nilmtk.pipeline import Contract

class TestContract(unittest.TestCase):

    def test_constructor(self):
        Contract(gaps_located=True)
        Contract(energy_computed=True)
        with self.assertRaises(TypeError):
            Contract(energy_computed='a')
        with self.assertRaises(ValueError):
            Contract(blah=1)

    def test_unsatisfied_conditions(self):
        preconditions = Contract(gaps_located=True, energy_computed=True)

        available = Contract(gaps_located=True)
        unsatisfied = preconditions.unsatisfied_conditions(available)
        self.assertEqual(len(unsatisfied), 1)

        available = Contract(gaps_located=True, energy_computed=False)
        unsatisfied = preconditions.unsatisfied_conditions(available)
        self.assertEqual(len(unsatisfied), 1)

        available = Contract(gaps_located=False, energy_computed=False)
        unsatisfied = preconditions.unsatisfied_conditions(available)
        self.assertEqual(len(unsatisfied), 2)

        available = Contract()
        unsatisfied = preconditions.unsatisfied_conditions(available)
        self.assertEqual(len(unsatisfied), 2)

        available = Contract(gaps_located=True, energy_computed=True)
        unsatisfied = preconditions.unsatisfied_conditions(available)
        self.assertEqual(unsatisfied, [])

    def test_repr(self):
        self.assertTrue(isinstance(str(Contract(gaps_located=True)), str))

if __name__ == '__main__':
    unittest.main()
