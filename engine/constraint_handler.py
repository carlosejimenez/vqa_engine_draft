import re
from . import utils


class ConstraintHandler:
    def __init__(self, objects):
        self.objects = objects

    def check_constraints(self, constraints, assignment):
        for constraint in constraints:
            func, argstr = re.match(r'^([a-zA-Z]\w+)\((.*)\)$', constraint).groups()
            args = argstr.replace(' ', '').split(',')
            keywords = {k: assignment[k] for k in assignment if k in args}
            if not getattr(self, func)(**keywords):
                return False
        return True

    def unique(self, **kwargs):
        # TODO: Implement relation uniqueness too!
        token_heads, token_nums = list(zip(*list(map(lambda x: re.match(r'^([a-z]+)(\d+)$', x).groups(), kwargs))))
        # ^ splits token types ('obj', 'attrs', ...) from token numbers.
        if len(set(token_nums)) != 1:
            raise AssertionError(f'Unique constraint received mixed object constraint.')
        token_num = token_nums[0]
        if 'rel' in token_heads:
            raise NotImplementedError(f'Unique constraint for relations is not implemented, yet!')
        obj_token = f'obj{token_num}'
        if not obj_token in kwargs:
            AssertionError(f'Unique constraint be related to an object token.')
        name = kwargs[obj_token]
        attrs_token = f'attrs{token_num}'
        attrs = frozenset() if attrs_token not in kwargs else kwargs[attrs_token]
        detection_count = 0
        for obj in self.objects.values():
            if obj['name'] == name:
                new_attrs = set(obj['attributes'])
                if attrs.issubset(new_attrs):
                    detection_count += 1
        return detection_count == 1

    def exclude_color(self, **kwargs):
        if len(kwargs) != 1:
            raise ValueError(f'exclude_color only accepts attrs tokens for one object at a time.')
        attr_list = set(list(kwargs.values())[0])
        return len(attr_list.intersection(utils.train_colors)) == 0
