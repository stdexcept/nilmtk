import abc
from contract import UnsatisfiedPreconditionsError

class Node(object):
    """Abstract class defining interface for all Node subclasses,
    where a 'node' is a module which runs pre-processing or statistics
    (or, later, maybe NILM training or disaggregation).
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.name = name

    def check_preconditions(conditions):
        """
        Parameters
        ----------
        conditions : nilmtk.Contract
        
        Raises
        ------
        UnsatistfiedPreconditionsError
        
        Description
        -----------
        
        Requirements can be of the form:
    
        "node X needs (power.apparent or power.active) (but not
        power.reactive) and voltage is useful but not essential"
    
        or
    
        "node Y needs everything available from disk (to save to a copy to
        disk)"
    
        or
    
        "ComputeEnergy node needs gaps to be bookended with zeros" (if
        none of the previous nodes provide this service then check
        source.metadata to see if zeros have already been inserted; if the
        haven't then raise an error to tell the user to add a
        BookendGapsWithZeros node.)
        """
        # If a subclass has complex rules for preconditions then
        # override this default method definition.
        unsatisfied_conditions = preconditions.unsatisfied_conditions(conditions)
        if unsatisfied_conditions:
            msg = str(self) + " not satisfied by:\n"
            msg += unsatisfied_conditions
            raise UnsatisfiedPreconditionsError(msg)
            
    def __repr__(self):
        return self.__class__.__name__ + ' ' + self.name

    @abc.abstractmethod
    def process(self, df):
        # check_preconditions again??? (in case this node is not run in
        # the context of a Pipeline?)
        # do stuff to df
        return df
