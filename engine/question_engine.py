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
from itertools import combinations, product
from .program_handlers import Handler
from .constraint_handler import ConstraintHandler
from . import utils


def assign_tokens(objects, token_set, constraints):
    """
    Returns a list of all possible token assignments (dictionaries).
    """
    constraint_handler = ConstraintHandler(objects)
    all_assignments = set()  # use set to absorb duplicates.
    for obj_ids in combinations(list(objects.keys()), len(token_set)):
        assignments = dict()
        for i in range(len(token_set)):
            token_obj_idx = str(i + 1)
            obj_i = objects[obj_ids[i]]
            for token in token_set[token_obj_idx]:
                key = f'{token}{token_obj_idx}'
                if token == 'obj':
                    val = [obj_i['name'], ]
                elif token == 'attrs':
                    val = list(map(frozenset, utils.powerset(obj_i['attributes'])))
                elif token == 'rel':
                    val = list(set(map(lambda x: x.get('name'), obj_i['relations'])))
                    # raise NotImplementedError('rel not implemented yet!')
                elif token == 'color':
                    # val = [utils.get_color(obj_i), ]  # wrapping list instantiates assignment_values even if
                                                        # utils.get_color(obj_i) is an empty frozenset.
                    val = utils.get_color(obj_i)        # Not wrapping instantiates the product of assignment values
                                                        # with individual elements of val, and only if len(val) != 0
                else:
                    raise ValueError(f'Token name unknown: {token}')
                assignments[key] = val
        key_list = list(assignments.keys())
        assignment_values = product(*[assignments[key] for key in key_list])
        for assignment in assignment_values:
            if constraint_handler.check_constraints(constraints, dict(zip(key_list, assignment))):
                all_assignments.add(zip(key_list, assignment))
    return list(map(dict, all_assignments))


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
        qa_pairs = set()  # FIXME: Set is used to remove duplicates, but there shouldn't be duplicates.
        for template, assignment in product(templates, token_assignments):
            try:
                template_idx = templates.index(template)
                question_data = f'{question_family["name"]}-{template_idx}'
                text = self.expand_text_template(template, assignment)
                answer = self.handler.get_answer(scene, program, assignment)
                qa_pairs.add((question_data, text, answer))
#                 print(f'{text}: {answer}')
            except Exception as e:
                print(e)
        return list(qa_pairs)

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
