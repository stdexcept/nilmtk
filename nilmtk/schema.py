from __future__ import print_function, division

class Schema(object):
    """A mechanism for ensuring that a dict conforms to a pre-defined schema.

    Examples
    --------
    >>> schema = Schema(name=str, exists=bool)
    >>> schema.validate({'name': 5})
    TypeError: Condition 'name=5' should be of <type 'str'>, not <type 'int'>.
    >> schema.validate({'blah': 5})
    ValueError: Condition 'blah' not in the schema.
    >> schema.validate({'name': 'John', 'exists':True})
    # If `validate()` raises no error then the dictionary has passed validation.
    """

    def __init__(self, **definition):
        for key, value in definition.iteritems():
            if not isinstance(value, type):
                error_msg = ("Schema.__init__ requires all kwarg values to"
                             " specify a *type* but `{}={}`."
                             .format(key, value))
                raise TypeError(error_msg)
        self.definition = definition

    def validate(self, dictionary):
        for key, value in dictionary.iteritems():
            try:
                expected_type = self.definition[key]
            except KeyError:
                error_msg = "Condition '{}' not in the schema.".format(key)
                raise ValueError(error_msg)

            if not isinstance(value, expected_type):
                error_msg = ("Condition '{}={}' should be of {}, not {}."
                             .format(key, value, expected_type, type(value)))
                raise TypeError(error_msg)
