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

all_stories = load_json('./preprocess/all_stories_train.json')
all_titles = load_json('./preprocess/all_titles_train.json')
all_story_counter = []
annotation_history = {}
'''
for i in range(len(all_titles)):
    t = all_titles[i]
    annotation_history[t] = []
    for x in all_stories[t]:
        dict = {}
        dict["s_id"] = x["id"]
        dict["label_time"] = 0
        dict["user"] = ""
        annotation_history[t].append(dict)
'''
for i in range (len(all_titles)):
    all_story_counter.append(str(i))
save_json('./preprocess/all_story_counter.json', all_story_counter)



