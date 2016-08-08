from flask import g

def get_calculation(func, cols):
    try:
        mod_class = __import__('iggybase.' + g.module + '.calculation',
                fromlist=[func])
        function = getattr(mod_class, func)
        calculation = function(cols)
    except (ImportError, AttributeError): # if module does not have calculation use mod_core
        if func in globals():
            function = globals()[func]
            #TODO: validate number or args or return None or False
            calculation = function(cols)
        else:
            calculation = None
    return calculation


def add(cols):
    return (cols[0] + cols[1])

def subtract(cols):
    return (cols[0] - cols[1])

def multiply(cols):
    return (cols[0] * cols[1])

def divide(cols):
    return (cols[0] / cols[1])

def percent(cols):
    return (float(cols[0]) * (cols[1]/100))

def chars(cols):
    if cols[0]:
        chars = len(str(cols[0]))
    else:
        chars = 0
    return chars

