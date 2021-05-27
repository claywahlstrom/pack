
"""
Decorators

"""

from clay.utils import qualify

def obsolete(func):
    """Decorator for warning the consumer the function is obsolete"""
    def inner(*args, **kwargs):
        print('Function {} is obsolete'.format(qualify(func)))
        return func(*args, **kwargs)
    return inner

def vintage(func):
    """Decorator for warning the consumer the function is vintage"""
    def inner(*args, **kwargs):
        print('Function {} is vintage'.format(qualify(func)))
        return func(*args, **kwargs)
    return inner
