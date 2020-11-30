import re
from . import utils


def terminal(is_terminal):
    """
    Decorator for handler functions, to specify if function can be terminal or not.
    """
    def wrapper(func):
        func.terminal = is_terminal
        return func
    return wrapper


class ConstraintHandler:
    def __init__(self, objects):
        self.objects = objects

    def check_constraints(self, constraints, assignment):
        for constraint in constraints:
            func, argstr = re.match(r'^([a-zA-Z]\w+)\((.*)\)$', constraint).groups()
            args = argstr.replace(' ', '').split(',')
            func_args = [assignment[a] if a in assignment.keys() else a for a in args]
            if not getattr(self, func)(*func_args):
                return False
        return True

    def unique(self, obj, attrs=None, rel=None):
        # TODO: Implement relation uniqueness too!
        if attrs is None:
            attrs = set()
        detected = 0
        for obj_i in self.objects.values():
            if obj_i['name'] == obj:
                new_attrs = set(obj_i['attributes'])
                if attrs.issubset(new_attrs):
                    detected += 1
        return detected == 1

    def max_length(self, attrs, max_len):
        return len(attrs) <= int(max_len)

    def exclude_color(self, attrs):
        return len(attrs.intersection(utils.train_colors)) == 0

    def not_equal(self, val1, val2):
        return val1 != val2
