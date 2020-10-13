# from pattern.en import wordnet

from collections import defaultdict
from itertools import chain, combinations


def powerset(x_iterable):
    x_set = set(x_iterable)
    return list(chain.from_iterable(combinations(x_set, r) for r in range(len(x_set) + 1)))


def get_attribute_map(obj_set):
    attr_obj_map = defaultdict(set)
    for obj_id, obj_data in obj_set.items():
        name = obj_data['name']  # string
        all_attrs = set(obj_data['attributes'])
        for attrs in powerset(all_attrs):
            key = (name, frozenset(attrs))  # (obj_name, {green, shiny, ...})
            attr_obj_map[key].add(obj_id)
    return dict(attr_obj_map)


def get_relations_map(obj_set):
    rel_obj_map = defaultdict(set)
    for obj_id, obj_data in obj_set.items():
        name = obj_data['name']  # string
        all_rels = set(map(lambda x: x.get('name'), obj_data['relations']))
        for rels in powerset(all_rels):
            key = (name, frozenset(rels))  # (obj_name, {to the left of, ...})
            rel_obj_map[key].add(obj_id)
    return dict(rel_obj_map)


# From checklist/text_generation.py #########################
# def all_synsets(word, pos=None):
#     map = {
#         'NOUN': wordnet.NOUN,
#         'VERB': wordnet.VERB,
#         'ADJ': wordnet.ADJECTIVE,
#         'ADV': wordnet.ADVERB
#         }
#     if pos is None:
#         pos_list = [wordnet.VERB, wordnet.ADJECTIVE, wordnet.NOUN, wordnet.ADVERB]
#     else:
#         pos_list = [map[pos]]
#     ret = []
#     for pos in pos_list:
#         ret.extend(wordnet.synsets(word, pos=pos))
#     return ret
#
#
# def clean_senses(synsets):
#     return [x for x in set(synsets) if '_' not in x]
#
#
# def all_possible_synonyms(word, pos=None):
#     ret = []
#     for syn in all_synsets(word, pos=pos):
#         # if syn.synonyms[0] != word:
#         #     continue
#         ret.extend(syn.senses)
#     return clean_senses(ret)
