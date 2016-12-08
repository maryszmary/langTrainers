
import re
from flask import Flask
from flask import render_template
from flask import request
import sqlite3


class TasksDB():

    def __init__(self, name):
        self.name = name
        self.db = sqlite3.connect(name)
        self.cursor = self.db.cursor()


    def get_tests(self, lang):
        self.cursor.execute('SELECT all FROM test WHERE language = ' + lang)
        return cur.fetchall()        


db = TasksDB('tasks.db')
app = Flask(__name__, static_folder=u"./static")


@app.route('/langtests/guest', methods=['GET', 'POST'])
def main_guest():
    if request.form and request.form['language'] != 'not chosen':
        # db.get_tests(request.form['language'])
        return render_template('main.html', chosen = True)
    else:
        return render_template('main.html')


@app.route('/langtests/loggedin')
def main_loggedin():
    return render_template('main_logged_in.html')


app.run(debug = True)  
