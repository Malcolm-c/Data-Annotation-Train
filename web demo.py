from flask import Flask, redirect, render_template, request, jsonify
import random
import csv
import json
import os, stat
from lemmatize import lemmatize

app = Flask(__name__, static_folder = './static')

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

def isLastSection(id, all_section_counter_original):
    if id not in all_section_counter_original:
        return True
    if all_section_counter_original.index(id) == len(all_section_counter_original) - 1:
        return True
    s_id1 = str(id).split('_')[0]
    s_id2 = str(all_section_counter_original[all_section_counter_original.index(id) + 1]).split('_')[0]
    if(s_id1 == s_id2):
        return False
    else:
        return True

def pick_a_paragraph(section_id_list, username):
    #pick a random paragraph from sections that haven't been annotated yet
    all_section_counter = load_json('./preprocess/all_section_counter.json')
    all_section_counter_original = load_json('./preprocess/all_section_counter_train_original.json')
    all_story_counter = load_json('./preprocess/all_story_counter.json')
    all_titles = load_json('./preprocess/all_titles_train.json')
    u_dict = load_json('./user_data/' + username + '.json')
    #check if there are sections left
    remain_sections = list(set(all_section_counter)-set(section_id_list))
    if remain_sections == []:
        return 0

    init_flag = 0
    if section_id_list == []:
        init_flag = 1
    #check if tsection_id_list is empty (initial)
    #check if it's the last section of a story
    if init_flag== 1 or isLastSection(section_id_list[len(section_id_list) - 1], all_section_counter_original):
        #pick a new story
        if (init_flag == 0):
            last_cnt_id = section_id_list[len(section_id_list) - 1]
            if (last_cnt_id.split("_")[0] in all_story_counter):
                all_story_counter.remove(last_cnt_id.split("_")[0])
                save_json('./preprocess/all_story_counter.json', all_story_counter)
        if all_story_counter != []:
            random_story_id = random.choice(all_story_counter)
            if (str(random_story_id) + '_0' in  all_section_counter):
                section_id = 0
                print("selected_section:", str(random_story_id) + '_' + str(section_id))
                title = all_titles[int(random_story_id)]
                return load_json('./preprocess/train_data/' + title + '.json')[str(section_id)]
            else:
                for story_id in all_story_counter:
                    if story_id + '_0' in  all_section_counter:
                        section_id = 0
                        print("selected_section:", str(random_story_id) + '_' + str(section_id))
                        title = all_titles[int(random_story_id)]
                        return load_json('./preprocess/train_data/' + title + '.json')[str(section_id)]
                return 0
        else:
            return 0
    else:
        #pick the next section
        last_cnt_id = section_id_list[len(section_id_list) - 1]
        story_id = int(last_cnt_id.split('_')[0])
        section_id = int(last_cnt_id.split('_')[1]) + 1
        print("selected_section:", str(story_id) + '_' + str(section_id))
        title = all_titles[story_id]
        return load_json('./preprocess/train_data/' + title + '.json')[str(section_id)]

@app.route('/new_paragraph', methods=["GET"])
def get_paragraph():
    if request.method == 'GET':
        story_title = str(request.args.get('title'))
        story_id = str(request.args.get('s_id'))
        para_id = str(request.args.get('id'))
        username = str(request.args.get('username'))
        print(story_title, para_id)
        ###########!!!!!!!!##########
        u_dict = load_json('./user_data/' + username + '.json')
        all_section_counter = load_json('./preprocess/all_section_counter.json')
        all_stories = load_json('./preprocess/all_stories_train.json')
        all_titles = load_json('./preprocess/all_titles_train.json')
        annotation_history = load_json('./preprocess/annotation_history.json')
        if (story_title != "" and para_id != 0 and u_dict['labeled_flag'] == 0):
            return "Haven't annotated!"
        if (u_dict['labeled_flag'] == 1):
            if story_title in all_titles:
                all_stories[story_title][int(para_id)]["label_time"] += 1
                annotation_history[story_title][int(para_id)]["label_time"] += 1
                if annotation_history[story_title][int(para_id)]["label_time"] > 0:
                    annotation_history[story_title][int(para_id)]["user"] = username
                    if (str(story_id) + '_' + str(para_id) in all_section_counter):
                        all_section_counter.remove(str(story_id) + '_' + str(para_id))
        save_json('./preprocess/all_section_counter.json', all_section_counter)
        #pick a new paragraph
        new_para_res = pick_a_paragraph(u_dict['section_id'], username)
        if new_para_res == 0:
            return "No more New Paragraphs"
        else:
            u_dict['para_dict'] = new_para_res
            u_dict['labeled_flag'] = 0
            save_json('./user_data/' + username + '.json', u_dict)
            return json.dumps(u_dict['para_dict'])

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/search', methods=["GET"])
def search_form():
    if request.method == 'GET':
        word = request.args.get('word')
        username = str(request.args.get('username'))
        u_dict = load_json('./user_data/' + username + '.json')
        u_dict['word'] = word.replace('"','').replace("'",'').replace('.','').replace(',','').lower()
        print("before:", u_dict['word'])
        #----lemmanization----#
        u_dict['word'] = lemmatize(u_dict['word'])
        print("after:", u_dict['word'])
        triples = load_json('./preprocess/triples_train.json')
        u_dict['retrieval'] = triples[u_dict['word']]
        save_json('./user_data/' + username + '.json', u_dict)
        return json.dumps(u_dict['retrieval'])

@app.route('/submit', methods=["GET"])
def submit_qa():
    if request.method == 'GET':
        question = str(request.args.get('question'))
        answer = str(request.args.get('answer'))
        concept = int(str(request.args.get('concept')))
        word_id = str(request.args.get('word_id'))
        title = str(request.args.get('title'))
        section = int(str(request.args.get('section')))
        username = str(request.args.get('username'))
        
        u_dict = load_json('./user_data/' + username + '.json')
        retireved_triplets = u_dict['retrieval']['triples']
        triple = retireved_triplets[concept]
        sub = triple[0]
        rel = triple[1]
        obj = triple[2]
        weight = triple[3]
        if not os.path.isdir('./QA dataset'):
            os.makedirs("./QA dataset")
        if not os.path.isdir('./QA dataset/' + username):
            os.makedirs('./QA dataset/' + username)  
        if not os.path.isfile("./QA dataset/" + username + '/' + title + "-QAC.csv"):
            f =  open("./QA dataset/" + username + '/' + title + "-QAC.csv", 'w', encoding='utf8', newline='')
            header = ['section_id', 'section_text', 'word_id', 'concept(sub)', 'relation', 'obj', 'question', 'answer']
            writer = csv.writer(f)
            writer.writerow(header)
            f.close()
        os.chmod("./QA dataset/" + username + '/' + title + "-QAC.csv", stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
        with open("./QA dataset/" + username + '/' + title + "-QAC.csv", 'a', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            all_stories = load_json('./preprocess/all_stories_train.json')
            text = all_stories[title][section]["text"]
            r = [section + 1, text, word_id, sub, rel, obj, question, answer]
            writer.writerow(r)
        u_dict['labeled_flag'] = 1
        all_titles = load_json('./preprocess/all_titles_train.json')
        section_id = str(all_titles.index(title)) + '_' + str(section)
        if (section_id not in u_dict['section_id']):
            u_dict['section_id'].append(section_id)
            u_dict['section_num'] += 1
            print("Sections updated, added " + section_id + ", now have " + str(u_dict['section_num']) + " sections.")
        save_json('./user_data/' + username + '.json', u_dict)
        return "done"

@app.route('/init', methods=["GET"])
def init():
    if request.method == 'GET':
        username = str(request.args.get('username')).lower()
        if not os.path.isdir('./user_data'):
            os.makedirs("./user_data")
        if not os.path.isfile('./user_data/' + username + '.json'):
            f = open('./user_data/' + username + '.json', 'w', encoding='utf8')
            u_dict = {}
            u_dict['labeled_flag'] = 0
            u_dict['word'] = ''
            u_dict['retrieval'] = {}
            u_dict['para_dict'] = {}
            u_dict['section_id'] = []
            u_dict['section_num'] = 0
            save_json('./user_data/' + username + '.json', u_dict)
        return "done"

if __name__ == '__main__':     
    app.run(debug = True, host = "0.0.0.0")

