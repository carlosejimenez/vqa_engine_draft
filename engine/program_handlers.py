from collections import defaultdict
from . import utils


def terminal(is_terminal):
    """
    Decorator for handler functions, to specify if function can be terminal or not.
    """
    def wrapper(func):
        func.terminal = is_terminal
        return func
    return wrapper


class Handler:
    def __init__(self):
        self._internal_dict = dict()

    def get_answer(self, scene, program_tree, token_assignment, verbose=False):
        """
        Evaluate an expression tree, as ['func_name', [arg1, arg2, ...]] recursively.
        """
        assert type(program_tree) in [tuple, list], TypeError(f'Received type {type(program_tree)} instead of tuple.')
        assert len(program_tree) == 2, AssertionError(f'Format error. Malformed branch.')
        # stack = [(program_tree, [])]
        # # token_assignment['scene'] = scene
        # results = []
        # while len(stack) > 0:
        #     evaluate = True
        #     (func, args), program_args = stack.pop()
        #     for ix, arg in enumerate(args):
        #         if type(arg) in [tuple, list]:
        #             if len(results) > 0:
        #                 val = results.pop()
        #                 program_args.append(val)
        #             else:
        #                 stack.append(((func, args), program_args))
        #                 stack.append((arg, []))
        #                 evaluate = False
        #                 break
        #         else:
        #             assert type(arg) is str, TypeError(f'Argument type not tuple or string.')
        #             if arg == 'scene':
        #                 val = scene
        #             else:
        #                 val = token_assignment[arg]
        #             program_args.append(val)
        #     if evaluate:
        #         result = getattr(self, func)(*program_args)
        #         results.append(result)
        # return results.pop()

        root, args = program_tree
        program_args = []
        token_assignment['scene'] = scene  # TODO: Remove from calls somehow.
        for arg in args:
            if type(arg) in [tuple, list]:
                val = self.get_answer(scene, arg, token_assignment)
            else:
                assert type(arg) is str, TypeError(f'Argument type not tuple or string.')
                val = token_assignment[arg]
            program_args.append(val)
        if verbose:
            print(f'Evaluating {root}(*{program_args}).')
        return getattr(self, root)(*program_args)

    @terminal(True)
    def equal(self, val1, val2):
        return val1 == val2

    @terminal(True)
    def member_of(self, element, in_set):
        return element in in_set

    @terminal(True)
    def exists(self, scene, obj_name, attributes):
        """
        Returns true if there is an object in scene with name == obj_name, and its attributes are a superset of attributes.
        """
        for obj_id, obj in scene['objects'].items():
            if obj['name'] == obj_name:
                if attributes.issubset(frozenset(obj['attributes'])):
                    return True
        return False

    @terminal(True)
    def convert_bool(self, val):
        return {True: 'yes', False: 'no'}[val]

    @terminal(True)
    def count(self, scene, obj_name, attributes):
        """
        Returns the number (int) of obj_name with attributes found in scene.
        """
        count = 0
        for obj_id, obj_data in scene['objects'].items():
            if obj_name == obj_data['name'] and attributes.issubset(set(obj_data['attributes'])):
                count += 1
        return count

    @terminal(True)
    def color(self, scene, obj_name, attributes):
        """
        Returns unique color of object.
        """
        colors = list(self.colors(scene, obj_name, attributes))
        if len(colors) == 1:
            return colors[0]
        # assert len(color) == 1, ValueError(f'No color attribute found for object: {attributes} {obj_name}.')
        else:
            return None

    @terminal(False)
    def colors(self, scene, obj_name, attributes):
        """
        Returns all colors of object.
        """
        attr_map = utils.get_attribute_map(scene['objects'])
        objs = attr_map[(obj_name, attributes)]
        if len(objs) != 1:
            return frozenset()
            # raise ValueError(f'FIXME: Constraints enforced for color.')
        obj_id = list(objs)[0]
        obj = scene['objects'][obj_id]
        return utils.get_color(obj)

    @terminal(False)
    def related_objs(self, scene, obj_name, rel_name):
        rel_map = utils.get_relations_map(scene['objects'])
        objs = rel_map[(obj_name, frozenset([rel_name]))]
        if len(objs) != 1:
            raise ValueError(f'FIXME: Constraints enforced for related_objs.')
        obj_id = list(objs)[0]
        relations = list(filter(lambda x: x['name'] == rel_name, scene['objects'][obj_id]['relations']))

        rel_objs_ids = list(map(lambda x: x['object'], relations))
        rel_objs = {'objects': {idx: scene['objects'][idx] for idx in rel_objs_ids}}
        return rel_objs
