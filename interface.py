
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
import sqlite3
import time

# idunno what's it for but well... (I added this following https://bitbucket.org/dendik/webdev/wiki/wsgi3tutorial)
# import pkgutil
# orig_get_loader = pkgutil.get_loader
# def get_loader(name):
#     try:
#         return orig_get_loader(name)
#     except AttributeError:
#         pass
# pkgutil.get_loader = get_loader
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


def count_score(form):
    results = []
    correct_ans = db.get_answers(session['task'])
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
    if 'done' in request.form:
        for el in request.form:
            session[el] = request.form[el]
        return redirect(url_for('results'))
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)


@app.route('/logged_in/testing', methods=['GET', 'POST'])
def testing_logged_in():
    tname = session['task']
    task, text, info, answers = process_task_req(tname)
    if 'done' in request.form:
        for el in request.form:
            session[el] = request.form[el]
        return redirect(url_for('results'))
    return render_template('test.html', tname = tname, test = text,
                           task = task, info = info)


@app.route('/results', methods=['GET', 'POST'])
def results():
    not_sents = ['action', 'language', 'task',  'csrfmiddlewaretoken',
                 'lang', 'done', 'username', 'password']
    form = {el : session[el] for el in session if el not in not_sents}
    results, score, total = count_score(form)
    if 'username' in session:
        db.write_resilts(session['username'], session['task'], score)
    return render_template('results.html', results = results,
                           score = score, total = total)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        username = session['username']
        results = db.get_stats(username)
        return render_template('profile.html', username = username,
                               results = results)
    return redirect(url_for('not_ready'))


@app.route('/not_ready', methods=['GET', 'POST'])
def not_ready():
    return render_template('not_ready.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.form and 'username' in request.form\
       and 'password' in request.form:
       if db.username_exists(request.form['username']):
          return render_template('register.html', error='AlreadyExists')
       else:
          db.add_user(request.form['username'], request.form['password'])
          session['username'] = request.form['username']
          return redirect(url_for('main_guest'))
    else:
        return render_template('register.html')


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if request.form and 'username' in request.form\
       and 'password' in request.form:
        if db.username_exists(request.form['username']):
            if not db.check_password(request.form['username'],
                                     request.form['password']):
                return render_template('log_in.html', error='DoesntFit')
            else:
                session['username'] = request.form['username']
                return redirect(url_for('main_guest'))
        else:
            return render_template('log_in.html', error='NoSuchUsername')
    else:
        return render_template('log_in.html')


if __name__ == '__main__':
    app.secret_key = 'toshcpri]7f2ba023b824h6[hs87nja5enact'
    app.run(debug = True, port = 5312)