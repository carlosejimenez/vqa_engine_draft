#!/usr/bin/env python
# coding: utf-8
import json
import argparse
from functools import reduce
from pprint import pprint as print


def unroll_dict(dictionary, key) -> list:
    """
        Unrolls dictionary by extracting key from dictionary values.

    """
    assert type(dictionary) is dict,TypeError(f'Dictionary passed is not type dict. Of type {type(dictionary)}')
    return list(map(lambda x: x[key], dictionary.values()))


def get_object_names(scene):
    return unroll_dict(scene['objects'], 'name')


def get_attribute_names(scene):
    all_attrs = unroll_dict(scene['objects'], 'attributes')
    if len(all_attrs) > 0:
        all_attrs = reduce(lambda x, y: set(x).union(y), all_attrs)
    return all_attrs


def main(scenes_file, vocab_type):
    data_prefix = scenes_file.split('.')[0]
    filename = f'{data_prefix}_{vocab_type}_vocab.json'
    # if filename is None:
    #     data_prefix = scenes_file.split('.')[0].split('_')[0]
    #     if data_prefix != '':
    #         filename = f'{data_prefix}_vocab.json'
    #     else:
    #         raise ValueError()

    get_set_func = {'attributes': get_attribute_names, 'objects': get_object_names}

    scenes = json.load(open(scenes_file, 'r'))
    vocab = set()
    for scene_id, scene in scenes.items():
        vocab = vocab.union(get_set_func[vocab_type](scene))

    json.dump(list(vocab), open(filename, 'w'), indent=4)
    print(f'Completed writing {filename}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'From a scene graphs file, extracts a vocabulary.')
    parser.add_argument('--scenes-file', type=str, required=True, help=f'Filepath to scenes JSON file.')
    parser.add_argument('--attributes', action='store_true', help=f'When included, saves attributes vocab.')
    parser.add_argument('--objects', action='store_true', help=f'When included, saves objects vocab.')
    # parser.add_argument('--output-filename', type=str, default=None, required=False, help='Vocabulary output '
    #                                                                                       'filename.')

    args = parser.parse_args()
    if args.attributes:
        main(args.scenes_file, 'attributes')
    if args.objects:
        main(args.scenes_file, 'objects')
