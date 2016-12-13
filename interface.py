
import re
from flask import Flask
from flask import render_template
from flask import request
import sqlite3

# idunno what's it for but well...
# import pkgutil
# orig_get_loader = pkgutil.get_loader
# def get_loader(name):
#     try:
#         return orig_get_loader(name)
#     except AttributeError:
#         pass
# pkgutil.get_loader = get_loade


class TasksDB():
    '''the db fith tests and users'''

    def __init__(self, name):
        self.name = name

    def get_tests(self, lang):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT * FROM tests WHERE language = ?', (lang, ))
        results = cur.fetchall()
        db.close()
        return results

    def get_task(self, topic, num):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT test, answers, info FROM tests WHERE'
                     ' ID = ? AND topic = ?', (num, topic))
        results = cur.fetchall()
        db.close()
        return results

    def get_answers(self, num):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT answers FROM tests WHERE ID = ?', (num, ))
        results = cur.fetchall()[0][0].split('\n')
        db.close()
        return results


def count_score(form, num):
    results = []
    correct_ans = db.get_answers(num)
    correct_ans = {el[0] : el[1] for el in enumerate(correct_ans)}
    form = {int(key) : form[key] for key in form if key != 'action'}
    for key in form:
        results.append([key, form[key].strip() == correct_ans[key].strip(),
                       form[key], correct_ans[key]])
    results = sorted(results, key = lambda x: x)
    score = sum([el[1] for el in results])
    results = [[line[0]] + [line[1]] + line[2:] for line in results]
    return results, score


def process_task_req(tname):
    num = int(tname.split('. ')[0]) - 1
    topic = tname.split('. ')[1]
    test = db.get_task(topic, num)
    text, answers, info = test[0]    
    text = text.split('\n')
    if '' in text:
        text.remove('')
    task = text[0]
    text = text[1:]
    text = [[str(i)] + text[i].split('[answer]') for i in range(len(text))]
    answers = answers.split('\n')
    return task, text, info, answers


db = TasksDB('tasks.db')
app = Flask(__name__, static_folder=u"./static")


@app.route('/', methods=['GET', 'POST'])
def main_guest():
    if request.form:
        if 'language' in request.form\
           and request.form['language'] != 'not chosen'\
           and 'task' not in request.form:
            lang = request.form['language']
            test_data = db.get_tests(lang)
            tests = [str(line[0] + 1) + '. ' + line[4] for line in test_data]
            return render_template('main.html', chosen = True, 
                                   tasks = tests)
        elif 'task' in request.form:
            tname = request.form['task']
            task, text, info, answers = process_task_req(tname)
            return render_template('test.html', tname = tname, test = text,
                                   task = task, info = info)
        elif 'action' in request.form:
            results, score = count_score(request.form, '0')
            return render_template('results.html', results = results,
                                   score = score)
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug = True)  