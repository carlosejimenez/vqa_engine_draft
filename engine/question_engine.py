# TODO: For generating negative examples, we want to extract a vocabulary of all object names from the scene graph data,
#       Also generate attribute vocabulary. Be sure not to generate ambiguous attribute combinations (black green cat).
# TODO: For an scene graph, generate an object-attribute map, where we construct a list of sets of objects, which are
#       conditioned by their attributes. So the key is a tuple of (frozenset(attributes), object_name), and values are
#       the oboject_id.
# TODO: Formalize question family json format, with program, token arguments, templates, constraints. Re-implement
#       token arguments to use obj_ids too, so we can apply constraints such as obj2['id'] != obj1['id']

"""
Inquiry types:
    Existence,
    Numeracy,
    Spatial Reasoning,
    Absolute spatial reasoning (with respect to the image dimensions (ie. is there a house in the bottom left corner?)),
    Compositionality,
    Taxonomy,
    Vocabulary,

"""
import re
from random import choice

from collections import defaultdict
from itertools import chain, combinations, combinations_with_replacement, product
from .program_handlers import Handler


def assign_tokens(objects, token_set, constraints):
    all_assignments = []
    for obj_ids in combinations(list(objects.keys()), len(token_set)):
        assignments = dict()
        for i in range(len(token_set)):
            idx = str(i + 1)
            obj_i = objects[obj_ids[i]]
            for token in token_set[idx]:
                key = f'{token}{idx}'
                if token == 'obj':
                    val = [obj_i['name'], ]
                elif token == 'attrs':
                    val = list(map(frozenset, powerset(obj_i['attributes'])))  # TODO: this is a test
                else:
                    raise ValueError(f'Token name unknown: {token}')
                assignments[key] = val
        key_list = list(assignments.keys())
        assignment_values = product(*[assignments[key] for key in key_list])
        for assignment in assignment_values:
            all_assignments.append(dict(zip(key_list, assignment)))
    return all_assignments


def powerset(x_iterable):
    return list(chain.from_iterable(combinations(x_iterable, r) for r in range(len(x_iterable) + 1)))


def get_attribute_map(obj_set):
    attr_obj_map = defaultdict(set)
    for obj_id, obj_data in obj_set.items():
        name = obj_data['name']  # string
        all_attrs = set(obj_data['attributes'])
        for attrs in powerset(all_attrs):
            key = (name, frozenset(attrs))  # (obj_name, {green, shiny, ...})
            attr_obj_map[key].add(obj_id)
    return dict(attr_obj_map)


class QGenerator:
    def __init__(self):
        self.handler = Handler()

    def generate_questions(self, scene, question_family, negative_examples=False):
        # attribute_map = get_attribute_map(scene['objects'])
        objects_present = set(map(lambda x: x['name'], scene['objects'].values()))
        tokens = question_family['tokens']
        constraints = question_family['constraints']
        token_sets = defaultdict(set)
        for token in tokens:
            match = re.match(r'^([a-z]+)(\d+)$', token)
            if not match:
                assert token == 'scene', AssertionError(f'Unrecognized special token: {token}.')
            assert len(match.groups()) == 2, AssertionError(f'Malformed input token.')
            token_type, object_number = match.groups()
            token_sets[object_number].add(token_type)
        program = question_family['program']
        templates = question_family['templates']
        token_assignments = assign_tokens(scene['objects'], token_sets, constraints)
        for template, assignment in product(templates, token_assignments):
            text = self.expand_text_template(template, assignment)
            print(f'{text}: {"Yes" if self.handler.get_answer(scene, program, assignment) else "No"}')

    @staticmethod
    def expand_text_template(template, assignment):
        def clean(string):
            return ' '.join(string.split())

        pattern = re.compile(r'(<([a-z]+\d+)>)')
        text = template
        for token, token_name in pattern.findall(template):
            value = assignment[token_name]
            if type(value) in [frozenset]:  # If value is a set of attributes.
                value = ' '.join(value)
            text = text.replace(token, value)
        return clean(text)
