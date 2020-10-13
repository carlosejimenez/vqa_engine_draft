#!/usr/bin/env python
# coding: utf-8
import json
import engine
import argparse
from pprint import pprint as print
from tqdm import tqdm


def main(question_family, scenes_file, short=False): 
    generator = engine.QGenerator()
    data_prefix = scenes_file.split('.')[0].split('_')[0]
    scenes = json.load(open(scenes_file, 'r'))
    if short:
        print(f'Truncating scene for testing.')
        scenes = {k: scenes[k] for k in list(scenes.keys())[:5]}
    question = json.load(open(f'question_families/{question_family}.json', 'r'))
    # program = question['program']
    # text_templates = question['templates']
    filename = f'{data_prefix}_{question_family}.txt'
    with open(filename, 'w+') as f:
        print(f'Starting {filename} ...')
        for scene_id, scene in tqdm(scenes.items()):
            qa_pairs = generator.generate_questions(scene, question)
            qa_pairs = list(map(lambda x: (scene_id, *x), qa_pairs))
            f.write('\n'.join(list(map(json.dumps, qa_pairs))))
            del scene
    print(f'Completed writing {filename}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--question-family', type=str, required=True, help=f'Name of question family, in ./question_'
                                                                           f'families. Not a filepath. Not a filename.')
    parser.add_argument('--scenes-file', type=str, required=True, help=f'Filepath to scenes JSON file.')
    parser.add_argument('--test', action='store_true', help=f'Only run on up to 5 scenes, for testing purposes.')

    args = parser.parse_args()
    main(args.question_family, args.scenes_file, args.test)
