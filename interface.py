
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
import sqlite3

# idunno what's it for but well... (I added this following https://bitbucket.org/dendik/webdev/wiki/wsgi3tutorial)
# import pkgutil
# orig_get_loader = pkgutil.get_loader
# def get_loader(name):
#     try:
#         return orig_get_loader(name)
#     except AttributeError:
#         pass
# pkgutil.get_loader = get_loade
# end of The Piece of Code I Don't Understand


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

    def get_task(self, topic):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT task, answers, info FROM tests WHERE'
                     ' topic = ?', (topic, ))
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
    total = len(results)
    results = [[line[0]] + [line[1]] + line[2:] for line in results]
    return results, score, total


def process_task_req(tname):
    test = db.get_task(tname)
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
            session['lang'] = lang
            test_data = db.get_tests(lang)
            tests = [line[1] for line in test_data]
            return render_template('main.html', chosen = True, 
                                   tasks = tests)
        elif 'task' in request.form:
            for el in request.form:
                session[el] = request.form[el]
            return redirect(url_for('testing'))
    return render_template('main.html')


@app.route('/testing', methods=['GET', 'POST'])
def testing():
    tname = session['task']
    task, text, info, answers = process_task_req(tname)
    if 'done' in session:
        return redirect(url_for('results'))
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)
    return render_template('not_ready.html')


@app.route('/results', methods=['GET', 'POST'])
def results():
    results, score, total = count_score(session, '0')
    return render_template('results.html', results = results,
                           score = score)


@app.route('/not_ready', methods=['GET', 'POST'])
def not_ready():
    return render_template('not_ready.html')


if __name__ == '__main__':
    app.secret_key = 'toshcpri]7f2ba023b824h6[hs87nja5enact'
    app.run(debug = True, port = 5312)