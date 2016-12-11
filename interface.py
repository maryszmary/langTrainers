
import re
from flask import Flask
from flask import render_template
from flask import request
import sqlite3


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


def count_score():
    pass


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
    return task, text


db = TasksDB('tasks.db')
app = Flask(__name__, static_folder=u"./static")


@app.route('/langtests/guest', methods=['GET', 'POST'])
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
            # num = int(tname.split('. ')[0]) - 1
            # topic = tname.split('. ')[1]
            # test = db.get_task(topic, num)
            # text, answers, info = test[0]
            task, text = process_task_req(tname)
            return render_template('test.html', tname = tname,
            	                   test = text, task = task)
    return render_template('main.html')


@app.route('/langtests/Russian')
def task():
    pass


@app.route('/langtests/loggedin')
def main_loggedin():
    return render_template('main_logged_in.html')


app.run(debug = True)  
