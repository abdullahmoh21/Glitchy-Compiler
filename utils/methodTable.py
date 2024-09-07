"""
Stores all member method data
Please note MOST of these methods have not been implemented. 
"""

from .ast import *

class MethodTable:
    METHODS = {
        'string': {
            'length': {
                'name': 'length',
                'parameters': [],
                'arity': 0,
                'return_type': 'integer'
            },
            'substring': {
                'name': 'substring',
                'parameters': [Parameter('', 'integer'), Parameter('', 'integer')],
                'arity': 2,
                'return_type': 'string'
            },
            'toUpperCase': {
                'name': 'toUpperCase',
                'parameters': [],
                'arity': 0,
                'return_type': 'string'
            },
            'toLowerCase': {
                'name': 'toLowerCase',
                'parameters': [],
                'arity': 0,
                'return_type': 'string'
            },
            'toInteger': {
                'name': 'toInteger',
                'parameters': [],
                'arity': 0,
                'return_type': 'integer'
            },
            'toDouble': {
                'name': 'toFloat',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'trim': {
                'name': 'trim',
                'parameters': [],
                'arity': 0,
                'return_type': 'string'
            }
        },
        'integer': {
            'abs': {
                'name': 'abs',
                'parameters': [],
                'arity': 0,
                'return_type': 'integer'
            },
            'toFloat': {
                'name': 'toFloat',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
                        'round': {
                'name': 'round',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'floor': {
                'name': 'floor',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'ceil': {
                'name': 'ceil',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            }
        },
        'double': {
            'abs': {
                'name': 'abs',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'toInteger': {
                'name': 'toInteger',
                'parameters': [],
                'arity': 0,
                'return_type': 'integer'
            },
            'round': {
                'name': 'round',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'floor': {
                'name': 'floor',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            },
            'ceil': {
                'name': 'ceil',
                'parameters': [],
                'arity': 0,
                'return_type': 'double'
            }
        }
    }

    @classmethod
    def getAll(cls, data_type):
        """ Returns a dict of methods for a given data type. """
        return cls.METHODS.get(data_type, {})

    @classmethod
    def get(cls, data_type, method_name):
        """ Returns the data for a given method of a specific type, or None if it does not exist. """
        return cls.METHODS.get(data_type, {}).get(method_name, None)
    