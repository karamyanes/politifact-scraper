import json
import pandas as ps
import sqlite3




with open('politifact.json') as f:
    dictionery = json.load(f)

antall = len(dictionery)
print(antall)

print(type(dictionery))


new_arr = []
question_database = {"model" : "game.question",'fields': {} }



pc=1
while pc <= antall:
    print(dictionery[0]['claim'])
    question_database = {"model" : "score.question", 'pk' : pc, 'fields': {"question_text": ''}}
    new_arr.append(question_database)
    pc += 1



print(new_arr)


    


    

    








"""
db = ps.DataFrame(data)
db.head()
db.columns
print(db)

items = []

for item in data:
    items.append(item['label'])
print(items)

items2= []
for item in data:
    items2.append(item['claim'])
print(items2)


def load_statements():
    with open("politifact.json") as json_file:
        pata = json.load(json_file)
    return pata

def load_statement_data(statement_id):
    data = load_statements()
    sdata = data[int(statement_id)]["label"]
    return sdata


load_statement_data(1)
"""