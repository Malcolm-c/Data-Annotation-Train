import os
import pandas as pd
import json
filepath = './train/'

all_stories = {}
all_titles = []
all_section_counter = []

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

for i, j, k in os.walk(filepath):
    for c, n in enumerate(k):
        if '-story.csv' in n:
            story_title = n[:len(n)-10]
            all_stories[story_title] = []
            story = pd.read_csv(filepath + n)
            all_titles.append(story_title)
            for index, row in story.iterrows():
                p_dict = {}
                paragraph = row["text"]
                p_dict["id"] = index
                p_dict["text"] = paragraph
                p_dict["label_time"] = 0
                all_stories[story_title].append(p_dict)
                all_section_counter.append(str(int((c-1)/2)) + '_' + str(index))

#file = open('all_stories_train.json', 'w')
#json.dump(all_stories, file)
save_json("./all_titles_train.json", all_titles)

#all_section_counter
#save_json('all_section_counter_train_original.json',{'0': all_section_counter})



