import json
import os
from lemmatize import lemmatize

filepath = './preprocess/data/'

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()
'''
triples = load_json('./preprocess/triples.json')
t1 = {}
for w in triples:
    if (len(w)<=2 and w != 'go' and w !='oh') or (triples[w]['triples'] == [] and w!= 'go' and w != 'oh'):
        continue
    t1[w] = triples[w]
save_json('triples_1.json', t1)
'''
triples = load_json('./triples_1.json')
for i, j, k in os.walk(filepath):
    for name in k:
        story_dict = load_json(filepath + name)
        for id in story_dict:
            words = story_dict[id]['words']
            for i, w_dict in enumerate(words):
                if w_dict['stop'] == 0:
                    w = lemmatize(w_dict['word'])
                    if (not w in triples):
                        story_dict[id]['words'][i]['stop'] = 1
        save_json(name, story_dict)

