"""
Simple dictionary that maps data types to their respective methods.
Placed here to avoid hardcoding the method names in multiple places.
Note: The method signatures do not include the 'self' or the implicit parameter.
"""

method_table = {
    'string': {
        'length': 'integer length()',
        'substring': 'string substring(integer start, integer length)',  # Explicit arguments required
        'toUpperCase': 'string toUpperCase()',  
        'toLowerCase': 'string toLowerCase()',  
        'toInteger': 'integer toInteger()',  
        'toFloat': 'float toFloat()',  
        'trim': 'string trim()'  
    },
    'integer': {
        'toString': 'string toString()',  
        'abs': 'integer abs()',  
        'toFloat': 'float toFloat()',  
        'isOdd': 'boolean isOdd()',  
        'isEven': 'boolean isEven()'  
    },
    'float': {
        'toString': 'string toString()',  
        'abs': 'float abs()',  
        'toInteger': 'integer toInteger()',  
        'round': 'float round()',  
        'floor': 'float floor()',  
        'ceil': 'float ceil()'  
    },
    'boolean': {
        'toString': 'string toString()',  
        'invert': 'boolean invert()'  
    }
}

# return the dict of methods for a given data type
def get_methods(data_type):
    return method_table.get(data_type, {})