# from pattern.en import wordnet
# from math import inf
import json
from collections import defaultdict
from itertools import chain, combinations, product

# attribute_vocabulary = json.load(open('../vocabs/train_sceneGraphs_attributes_vocab.json', 'r'))
# object_vocabulary = json.load(open('../vocabs/train_sceneGraphs_objects_vocab.json', 'r'))
train_colors = {'translucent', 'gray', 'chrome', 'dark brown', 'blue', 'navy', 'pink', 'teal', 'calico', 'tan',
                'blond', 'plaid', 'yellow', 'red', 'silver', 'brass', 'cream colored', 'dark blue',
                'black and white', 'khaki', 'dark colored', 'purple', 'beige', 'orange', 'black', 'bronze', 'green',
                'maroon', 'light brown', 'white', 'light blue', 'rainbow colored', 'gold', 'brown', 'light colored'}


def powerset(x_iterable, max_depth=None):
    x_set = set(x_iterable)
    if max_depth == None:
        max_depth = len(x_set)
    return list(chain.from_iterable(combinations(x_set, r) for r in range(max_depth + 1)))


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


def param_grid(token_dict):
    for p in token_dict:
        items = sorted(p.items())
        if not items:
            yield {}
        else:
            keys, values = zip(*items)
            for v in product(*values):
                params = dict(zip(keys, v))
                yield params


def get_assignments(token_dict, max_depth=1):
    for token in token_dict:
        if token.startswith('attrs'):
            token_dict[token] = list(map(lambda x: ' '.join(x), powerset(token_dict[token], max_depth)))
    return list(param_grid([token_dict]))


def get_color(obj):
    attributes = set(obj['attributes'])
    colors = attributes.intersection(train_colors)
    return frozenset(colors)



## From checklist/text_generation.py #########################
# def all_possible_hypernyms(word, pos=None, depth=None):
#     ret = []
#     for syn in all_synsets(word, pos=pos):
#         ret.extend([y for x in syn.hypernyms(recursive=True, depth=depth) for y in x.senses])
#     return clean_senses(ret)
#
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
