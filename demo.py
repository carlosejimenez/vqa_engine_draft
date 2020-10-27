#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import engine
from IPython.display import display
from PIL import Image
from pprint import pprint as print
from tqdm import tqdm


# In[41]:


generator = engine.QGenerator()
data_prefix = 'val'
scenes = json.load(open(f'{data_prefix}_sceneGraphs.json', 'r'))
img_ids = set(json.load(open('valid_img_ids.json')))
scenes = {k: scenes[k] for k in list(scenes.keys()) for k in img_ids}


# In[42]:


assert set(scenes.keys()) == img_ids


# In[77]:


question_family = 'color_query_bool'
question = json.load(open(f'question_families/{question_family}.json', 'r'))
program = question['program']
text_templates = question['templates']


# In[78]:


# scene_id, scene = list(scenes.items())[0]
# print(list(map(lambda x: (x.get('name'), x.get('attributes')), scene['objects'].values())))


# In[80]:


print(question['templates'])


# In[81]:


# assignment = {'obj1': 'man', 'attrs1': frozenset([])}
# print(generator.expand_text_template(text_templates[0], assignment))
# print('Yes' if generator.handler.get_answer(scene, program, assignment) else 'No')


# In[82]:


# assignment = {'obj1': 'man', 'attrs1': frozenset(['tall'])}
# print(generator.expand_text_template(text_templates[1], assignment))
# print('Yes' if generator.handler.get_answer(scene, program, assignment) else 'No')


# In[83]:


# assignment = {'obj1': 'bike', 'attrs1': frozenset(['white'])}
# print(generator.expand_text_template(text_templates[2], assignment))
# print('Yes' if generator.handler.get_answer(scene, program, assignment) else 'No')


# In[84]:


# question = json.load(open(f'question_families/simple_numeracy.json', 'r'))
# program = question['program']
# text_templates = question['templates']


# In[85]:


# assignment = {'obj1': 'sign', 'attrs1': frozenset(['blue'])}
# print(generator.expand_text_template(text_templates[0], assignment))
# print(generator.handler.get_answer(scene, program, assignment))


# In[86]:


# assignment = {'obj1': 'sign', 'attrs1': frozenset(['red'])}
# print(generator.expand_text_template(text_templates[1], assignment))
# print(generator.handler.get_answer(scene, program, assignment))


# In[87]:


# display(Image.open(f'images/{scene_id}.jpg'))


# In[88]:


question


# In[89]:


# with open(f'{data_prefix}_{question_family}.txt', 'w+') as f:
d_names = ['question_id', 'img_id', 'label', 'sent']
bool_binary = {True: 'yes', False: 'no'}
all_questions = []
for img_id, scene in tqdm(scenes.items()):
#     qa_pairs = list(map(lambda x: dict(zip(d_names, (img_id, *x))), qa_pairs))
    for ix, (question_type, sent, answer, assignment) in enumerate(generator.generate_questions(scene, question)):
        q_id = str(img_id) + str(len(all_questions)).zfill(9)
        answer_dict = {answer: 1.0}
        obj = scene['objects'][dict(assignment)['obj1_id']]
        assignment = dict(assignment)
        for arg in assignment:
            if type(assignment[arg]) == frozenset:
                assignment[arg] = sorted(assignment[arg])
        assignment = sorted(assignment.items())
        question_dict = {'img_id': img_id,
                         'label': answer_dict,
                         'question_id': q_id,
                         'sent': sent,
                         'assignment': assignment,
                         'question_type': question_type}
        all_questions.append(question_dict)


# In[ ]:


json.dump(all_questions, open(f'{question_family}.json', 'w+'))


# In[ ]:





# In[ ]:




