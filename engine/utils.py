# from pattern.en import wordnet
# from math import inf
import os
import json
import numpy as np
import random
from collections import defaultdict, OrderedDict
from itertools import chain, combinations, product

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
attribute_vocabulary = set(json.load(open(os.path.join(ROOT_DIR, 'vocabs', 'train_sceneGraphs_attributes_vocab.json'),
                                          'r')))
object_vocabulary = set(json.load(open(os.path.join(ROOT_DIR, 'vocabs', 'train_sceneGraphs_objects_vocab.json'), 'r')))
train_obj_colors = json.load(open(os.path.join(ROOT_DIR, 'vocabs', 'train_obj_color_pair_dists.json')))
train_colors = OrderedDict([
    ('white', 0.2425825132406033), ('black', 0.1560781110508968), ('green', 0.11689692095431828),
    ('blue', 0.11319243184656347), ('brown', 0.09067751571462605), ('red', 0.06931976155133009),
    ('gray', 0.05832934086274017), ('yellow', 0.039157627975045094), ('orange', 0.026245585374729364),
    ('silver', 0.020920545908175794), ('pink', 0.01895179975338313), ('tan', 0.008893391872115276),
    ('purple', 0.008492835806047087), ('blond', 0.006102589477156523), ('gold', 0.004505601239891195),
    ('beige', 0.003120672096426673), ('plaid', 0.002280289761734591), ('light brown', 0.0018352274661032702),
    ('light blue', 0.001377075102953381), ('dark brown', 0.0013666030489385265),
    ('cream colored', 0.0013011527113456851), ('light colored', 0.0012199942927305619),
    ('maroon', 0.001136217860611725), ('dark blue', 0.0010602954690040291), ('black and white', 0.0009869910909000468),
    ('chrome', 0.0009372488343294875), ('dark colored', 0.0007670779565881001), ('khaki', 0.0007461338485583908),
    ('rainbow colored', 0.0004319722281127526), ('teal', 0.0003874659985496205), ('navy', 0.00035866785000877036),
    ('brunette', 0.0002618013503713652), ('translucent', 7.854040511140956e-05)
])


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
    # return dict(attr_obj_map)  # TODO: Do we need a proper dict? (not defaultdict)
    return attr_obj_map


def get_count(obj_dict, obj_name, obj_attrs):
    count = 0
    for obj_id, obj_data in obj_dict.items():
        if obj_name == obj_data['name'] and obj_attrs.issubset(set(obj_data['attributes'])):
            count += 1
    return count


def get_random_count(exclude):
    if type(exclude) not in [set, frozenset, list]:
        exclude = frozenset([exclude, ])
    count = random.choice(list(filter(lambda x: x not in exclude, range(1, 16))))
    return count


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
    colors = attributes.intersection(train_colors.keys())
    return frozenset(colors)


def get_random_color(obj, exclude=None):
    exclude = frozenset() if exclude is None else exclude
    assert type(exclude) in [frozenset, set], AssertionError(f'exclude argument passed not frozenset.')
    color_dict = train_colors if obj['name'] not in train_obj_colors else train_obj_colors[obj['name']]
    if len(color_dict) < 2:
        color_dict = train_colors
    filter_colors = {k: color_dict[k] for k in filter(lambda x: x not in exclude, color_dict)}

    # ranked - get first/best
    # color = list(filter_colors.keys())[0]

    # probabilistic
    z = sum(filter_colors.values())
    filter_colors = {k: v / z for k, v in filter_colors.items()}  # re-normalize
    color = np.random.choice(list(filter_colors.keys()), size=1, p=list(filter_colors.values()))[0]
    return frozenset([color, ])


def get_random_attrs():
    num_attrs = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
    attrs = random.sample(attribute_vocabulary, k=num_attrs)
    return frozenset(attrs)


def get_random_obj_name():
    return random.choice(list(object_vocabulary))


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
