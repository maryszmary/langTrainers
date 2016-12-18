
import lxml.etree
import os
import sqlite3


def creation(dbname):
    """checks, if there is one with the same name,
    if there is, deletes it and creates a new one"""
    if os.path.exists(dbname):
        os.system('rm ' + dbname)
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE tests (ID integer, topic, task, '
                   'answers, info, language)')
    cursor.execute('CREATE TABLE users (ID integer, username, password, '
                   'tests_passed)')
    cursor.execute('CREATE TABLE stats (ID integer, time, '
                   'test_num, user, score)')
    db.commit()
    return db, cursor


def load_data(cursor, db):
    i = 0
    for pair in [('rusdata.xml', 'Russian'), ('engdata.xml', 'English')]:
        data = get_data(*pair)
        for task in data:
            task.insert(0, str(i))
            cursor.execute('INSERT INTO tests VALUES (?, ?, ?, ?, ?, ?)',
                            tuple(task))
            i += 1
    db.commit()


def get_data(fname, lang):
    with open(fname, 'r') as f:
        tasks = lxml.etree.fromstring(f.read())
    data = []
    for unit in tasks:
        test, answers = task_parser(unit.xpath('.//test')[0].text.strip())
        name = unit.xpath('.//name')[0].text
        theory = unit.xpath('.//theory')[0].text
        data.append([name, test, answers, theory, lang])
    return data


def task_parser(text):
    task = text.split('\n', 1)[0]
    answers = ''
    for line in text.split('\n')[1:]:
        if not line.startswith('%') and line != '':
            task += line.split('#')[0].strip() + '\n'
            try:
                answers += line.split('#')[1] + '\n'
            except IndexError:
                print('IndexError, ' + line)
    return task, answers


def main():
    db, cursor = creation('tasks.db')
    load_data(cursor, db)


main()
