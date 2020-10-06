import json
from functools import reduce
from engine import assign_tokens


def test_assign_tokens():
    objs = json.load(open('tests/resources/sample_objects.json'))
    token_set = {'1': ['obj', 'attrs'], '2': ['obj', 'attrs']}
    assignments = assign_tokens(objs, token_set, None)
    expected_number_of_elements_per_assignment = reduce(lambda x, y: x * y, list(map(len, token_set.values())))
    # assert all(list(map(lambda x: len(x) == expected_number_of_elements_per_assignment, assignments))), \
    #     AssertionError(f'engine.question_engine.assign_tokens returned an assignment of incorrect length.')
    token_keys = {f'{vi}{k}' for k, v in token_set.items() for vi in v}
    assert all(list(map(lambda x: set(x.keys()) == token_keys, assignments))), AssertionError(f'Some assignments have'
                                                                                              f'incorrect key values.')
