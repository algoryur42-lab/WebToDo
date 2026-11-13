import sqlite3
from contextlib import closing
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_wtf.csrf import CSRFProtect

def init_db():
    with closing(sqlite3.connect("tasks.db")) as conn, conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0,1))
            )
            ''')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'секретный-ключ-для-защиты'

csrf = CSRFProtect(app)

@app.route('/')
def index():
    show_open = request.args.get('show') == 'open'
    with closing(sqlite3.connect("tasks.db")) as conn, conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if show_open:
            cursor.execute('SELECT * FROM tasks WHERE done = 0 ORDER BY id')
        else:
            cursor.execute('SELECT * FROM tasks ORDER BY id')
        tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks, show_open=show_open)

@app.route('/done', methods=["POST"])
def change_done():
    task_id = request.form.get('id_done', 0, type=int)
    with closing(sqlite3.connect("tasks.db")) as conn, conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET done = NOT done WHERE id = ?', (task_id,))
        if not cursor.rowcount:
            abort(404)
    return redirect(url_for('index'))

@app.route('/add', methods=["POST"])
def add_task():
    title = request.form.get('title', '').strip()
    if title:
        with closing(sqlite3.connect("tasks.db")) as conn, conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
    return redirect(url_for('index'))

@app.route('/delete', methods=["POST"])
def delete_task():
    task_id = request.form.get('id_delete', 0, type=int)
    with closing(sqlite3.connect('tasks.db')) as conn, conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        if not cursor.rowcount:
            abort(404)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)