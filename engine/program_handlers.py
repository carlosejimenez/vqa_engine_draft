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
        Evaluate an expression tree, as {'func_name': [args list]} recursively.
        """
        assert type(program_tree) in [tuple, list], TypeError(f'Received type {type(program_tree)} instead of tuple.')
        assert len(program_tree) == 2, AssertionError(f'Format error. Malformed branch.')
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
    def exists(self, scene, obj_name, attributes):
        """
        Returns true if there is an object in scene with name == obj_name, and its attributes are a superset of attributes.
        """
        for obj_id, obj in scene['objects'].items():
            if obj['name'] == obj_name:
                if attributes.issubset(frozenset(obj['attributes'])):
                    return True
        return False
