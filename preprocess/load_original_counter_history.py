import os
import pandas as pd
import json

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

all_stories = load_json('./all_stories.json')
all_titles = load_json('./all_titles.json')
all_section_counter = []
annotation_history = {}

for i, t in enumerate(all_titles):
    s_list = all_stories[t]
    #annotation_history[t] = []
    for j, s in enumerate(s_list):
        all_section_counter.append(str(i) + '_' + str(s['id']))
        '''annotation_history[t].append({
            "s_id": s['id'],
            "label_time": 0,
            "user1": "",
            "user2": ""
        })'''

#file = open('annotation_history_original.json', 'w')
#json.dump(annotation_history, file)

file = open('./all_section_counter_original.json', 'w')
file.close()
#json.dump({'0': all_section_counter}, file)
save_json('./all_section_counter_original.json',{'0': all_section_counter})


