
import sqlite3
import os


def creation(dbname):
    """checks, if there is one with the same name,
    if there is, deletes it and creates a new one"""
    if os.path.exists(dbname):
        os.system('rm ' + dbname)
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE tests (ID integer, test, answers, '
    	           'info, topic, language)')
    cursor.execute('CREATE TABLE users (ID integer, username, password, '
    	           'tests_passed)')
    cursor.execute('CREATE TABLE stats (ID integer, time, '
    	           'test_num, user, score)')
    db.commit()
    return db, cursor


def load_data(cursor, db):
	i = 0
	for pair in [('rusdata', 'Russian')]:
		data = get_data(*pair)
		for task in data:
			cursor.execute('INSERT INTO tests VALUES (?, ?, ?, ?, ?, ?)',
			               (i, task[2], '', task[1], task[0], task[3]))
			i += 1
	db.commit()


def get_data(fname, lang):
	with open(fname, 'r') as f:
		tasks = f.read().split('@')
	tasks = [[task.split('\n')[1], task.split('***')[0], task.split('***')[1]]
	         for task in tasks]
	tasks = [line + [lang] for line in tasks]
	return tasks


def main():
	db, cursor = creation('tasks.db')
	load_data(cursor, db)


main()
