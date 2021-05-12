new_dict = {}
question_database = {'banana':3,'apple':2, 'mango':1, 'kiwi':5}

antall = 10
new_arr = []
pc = 1
while pc <= antall:
    question_database = {'banana':3, 'apple':2, 'mango':1, 'kiwi':5, 'pk': pc}
    new_arr.append(question_database)
    pc += 1

# print(question_database)
print(new_arr)