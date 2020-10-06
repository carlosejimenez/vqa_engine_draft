import argparse
import json
import os
import engine


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene-graph-file', type=str, help=f'JSON file containing a dictionary of scene graphs.')
    parser.add_argument('-q', '--question-family-dir', type=str, help='Directory with JSON question family '
                                                                            'files.')
    args = parser.parse_args()
    graphs = json.load(open(args.scene_graph_file, 'r'))

    question_files = list(filter(lambda x: x.endswith('.json'), os.listdir(args.question_family_dir)))
    questions = map(lambda x: json.load(open(os.path.join(args.question_family_dir, x), 'r')), question_files)

    generator = engine.QGenerator()

    for scene_id, scene in graphs.items():
        for question in questions:
            generator.generate_questions(scene, question)
