import abc

class Node(object):
    """Abstract class defining interface for all Node subclasses,
    where a 'node' is a module which runs pre-processing or statistics
    (or, later, maybe NILM training or disaggregation).
    """

    __metaclass__ = abc.ABCMeta

    postconditions =  {} # TODO

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def check_preconditions(conditions):
        """ Static method

        Parameters
        ----------
        conditions : dict
        
        Returns
        -------
        boolean
        
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
        # TODO: see if there are any unsatisfied preconditions
        # if there are then raise an UnsatisfiedPreconditionsError
        # giving the exact precondition that failed, why it failed
        # which node is complaining, and suggestions for how to fix it
        pass

    @abc.abstractmethod
    def process(self, df):
        # check_preconditions again??? (in case this node is not run in
        # the context of a Pipeline?)
        # do stuff to df
        pass
