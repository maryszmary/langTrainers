
import re
from flask import Flask
from flask import render_template
from flask import request
import sqlite3


class TasksDB():

    def __init__(self, name):
        self.name = name


    def get_tests(self, lang):
        db = sqlite3.connect(self.name)
        cur = db.cursor()
        cur.execute('SELECT * FROM tests WHERE language = ?', (lang, ))
        results = cur.fetchall()
        db.close()
        return results     


db = TasksDB('tasks.db')
app = Flask(__name__, static_folder=u"./static")


@app.route('/langtests/guest', methods=['GET', 'POST'])
def main_guest():
    if request.form and request.form['language'] != 'not chosen':
        lang = request.form['language']
        test_data = db.get_tests(lang)
        tests = [str(line[0] + 1) + ' ' + line[4] for line in test_data]
        return render_template('main.html', chosen = True, 
                               lang = lang, tasks = tests)
    else:
        return render_template('main.html')


@app.route('/langtests/loggedin')
def main_loggedin():
    return render_template('main_logged_in.html')


app.run(debug = True)  
