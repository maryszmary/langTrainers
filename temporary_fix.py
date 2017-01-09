
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import sqlite3
import time

# idunno what's it for but well... (I added this following https://bitbucket.org/dendik/webdev/wiki/wsgi3tutorial)
import pkgutil
orig_get_loader = pkgutil.get_loader
def get_loader(name):
    try:
        return orig_get_loader(name)
    except AttributeError:
        pass
pkgutil.get_loader = get_loader
# end of The Piece of Code I Don't Understand

NOT_SENTS = ['action', 'language', 'task',  'csrfmiddlewaretoken', 'lang', 'done']
TASKS = {'Задание 1. Формы.': 0, 'Задание 2. Фреймы и формы.' : 1, 
         'Задание 3. Устойчивые сочетания' : 2, 'Задание 4. Конструкции' : 3,
         'Frames. Task 1.': 4, 'Constructions&Idioms. Task 2.' : 5,
         'Word formation. Task 3.' : 6}
REV_TASKS = {TASKS[el] : el for el in TASKS}


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

    def get_answers(self, tname):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT answers FROM tests WHERE topic = ?', (tname, ))
        results = cur.fetchall()[0][0].split('\n')
        results = {el[0] : el[1].split('|') for el in enumerate(results)}
        results = {key : [i.strip() for i in results[key]] for key in results}
        db.close()
        return results

    def username_exists(self, username):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT username FROM users WHERE username = ?',
                    (username, ))
        results = cur.fetchall()
        db.close()
        return len(results) > 0


    def add_user(self, username, password):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT ID FROM users')
        ids = [line[0] for line in cur.fetchall()]
        if ids:
            new_id = max(ids) + 1
        else:
            new_id = 0
        cur.execute('INSERT INTO users VALUES (?, ?, ?, NULL)',
                    (new_id, username, password))
        db.commit()
        db.close()


    def check_password(self, username, password):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT password FROM users WHERE username = ?',
                    (username, ))
        stored_password = cur.fetchall()[0][0]
        db.close()
        return stored_password == password

    def write_resilts(self, username, tname, score):
        current_time = time.clock()
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT ID FROM stats')
        ids = [line[0] for line in cur.fetchall()]
        if ids:
            new_id = max(ids) + 1
        else:
            new_id = 0
        cur.execute('INSERT INTO stats VALUES (?, ?, ?, ?, ?)',
                    (new_id, current_time, tname, username, score))
        db.commit()
        cur.execute('UPDATE users SET tests_passed = tests_passed || "," || ?'
                    'WHERE username = ? ', (str(new_id), username))
        db.commit()
        db.close()

    def get_stats(self, username):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT * FROM stats WHERE user = ?', (username, ))
        results = cur.fetchall()
        db.commit()
        db.close()
        return results


def count_score(form, lang):
    results = []
    correct_ans = db.get_answers(lang)
    form = {int(key) : form[key].lower().replace('ё', 'е') for key in form}
    for key in form:
        results.append([key, form[key].strip() in correct_ans[key],
                       form[key], ' | '.join(correct_ans[key])])
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
           and request.form['language'] != 'not chosen':
            lang = request.form['language']
            test_data = db.get_tests(lang)
            tests = [line[1] for line in test_data]
            if 'task' not in request.form:
                return render_template('main.html', chosen = True, 
                                       tasks = tests)
            else:
                return redirect(url_for('t' + str(TASKS[request.form['task']])))
    return render_template('main.html')


@app.route('/russian/0', methods=['GET', 'POST'])
def t0():
    tname = REV_TASKS[0]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results, score = score, total = total)
    return render_template('test.html', tname = tname, test = text, task = task, info = info)

@app.route('/russian/1', methods=['GET', 'POST'])
def t1():
    tname = REV_TASKS[1]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results, score = score, total = total)
    return render_template('test.html', tname = tname, test = text, task = task, info = info)


@app.route('/russian/2', methods=['GET', 'POST'])
def t2():
    tname = REV_TASKS[2]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results, score = score, total = total)
    return render_template('test.html', tname = tname, test = text, task = task, info = info)


@app.route('/russian/3', methods=['GET', 'POST'])
def t3():
    tname = REV_TASKS[3]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results, score = score, total = total)
    return render_template('test.html', tname = tname, test = text, task = task, info = info)


@app.route('/english/4', methods=['GET', 'POST'])
def t4():
    tname = REV_TASKS[4]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results,
                           score = score, total = total)
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)

@app.route('/english/5', methods=['GET', 'POST'])
def t5():
    tname = REV_TASKS[5]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results,
                           score = score, total = total)
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)


@app.route('/english/6', methods=['GET', 'POST'])
def t6():
    tname = REV_TASKS[6]
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        form = {el : request.form[el] for el in request.form if el not in NOT_SENTS}
        results, score, total = count_score(form, tname)
        return render_template('results.html', results = results,
                           score = score, total = total)
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)


@app.route('/not_ready', methods=['GET', 'POST'])
def not_ready():
    return render_template('not_ready.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return redirect(url_for('not_ready'))


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    return redirect(url_for('not_ready'))


if __name__ == '__main__':
    app.run(debug = True, port = 5312)