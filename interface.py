
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

    def get_task(self, lang, name):
        pass  


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
                                   lang = lang, tasks = tests)
        elif 'task' in request.form:
            task_name = request.form['task']
            task_id = int(task_name.strip('.'))
            return render_template('test.html', test_name = task_name)
    return render_template('main.html')


@app.route('/langtests/loggedin')
def main_loggedin():
    return render_template('main_logged_in.html')


app.run(debug = True)  
