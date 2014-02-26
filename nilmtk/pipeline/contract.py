from __future__ import print_function, division
from nilmtk import Schema

CONTRACT_SCHEMA = Schema(
    gaps_bookended_with_zeros=bool,
    gaps_located=bool,
    energy_computed=bool)

class UnsatisfiedPreconditionsError(Exception):
    pass

class Contract(object):
    """
    Mechanism for checking pre- and post-conditions for Nodes.

    Attributes
    ----------
    _conditions : dict

    Examples
    --------
    >>> preconditions = Contract(gaps_located=True)
    >>> preconditions.unsatisfied_conditions(Contract(gaps_located=False))
    ["Requires 'gaps_located=True' not 'gaps_located=False'."]

    """

    def __init__(self, **kwargs):
        self.conditions = kwargs

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, new_conditions):
        """
        Parameters
        ----------
        new_conditions : dict
        """
        # Check the new conditions comply with CONTRACT_SCHEMA
        CONTRACT_SCHEMA.validate(new_conditions)
        self._conditions = new_conditions

    def unsatisfied_conditions(self, other):
        """
        Parameters
        ----------
        other : Contract

        Returns
        -------
        list of strings describing (for human consumption) which 
        conditions are not satisfied.  If all conditions are satisfied
        then returns an empty list.
        """
        unsatisfied_conditions = []
        for key, value in self.conditions.iteritems():
            try:
                other_value = other.conditions[key]
            except KeyError:
                msg = ("Requires '{}={}' but '{}' not in conditions."
                       .format(key, value, key))
                unsatisfied_conditions.append(msg)
            else:
                if other_value != value:
                    msg = ("Requires '{}={}' not '{}={}'."
                           .format(key, value, key, other_value))
                    unsatisfied_conditions.append(msg)

        return unsatisfied_conditions

    def __repr__(self):
        return self.__class__.__name__ + ' ' + str(self.conditions)

