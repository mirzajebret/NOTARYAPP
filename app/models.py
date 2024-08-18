import sqlite3
from flask import jsonify
import os
from docx import Document
import pandas as pd

def init_db():
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY, filename TEXT, content TEXT, path TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY, task TEXT, completed BOOLEAN)''')
    conn.commit()
    conn.close()

def get_document_counts():
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    c.execute("SELECT category, COUNT(DISTINCT filename) FROM files GROUP BY category")
    data = dict(c.fetchall())
    conn.close()
    return data

def manage_todos_db(request):
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    if request.method == 'POST':
        task = request.json.get('task')
        c.execute('INSERT INTO todos (task, completed) VALUES (?, ?)', (task, False))
        conn.commit()
        new_todo = {'id': c.lastrowid, 'task': task, 'completed': False}
        conn.close()
        return jsonify(new_todo), 201
    else:
        c.execute('SELECT * FROM todos')
        todos = [{'id': row[0], 'task': row[1], 'completed': row[2]} for row in c.fetchall()]
        conn.close()
        return jsonify(todos)

def update_or_delete_todo_db(todo_id, request):
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    if request.method == 'PUT':
        completed = request.json.get('completed')
        c.execute('UPDATE todos SET completed = ? WHERE id = ?', (completed, todo_id))
        conn.commit()
        conn.close()
        return '', 204
    elif request.method == 'DELETE':
        c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()
        return '', 204

def category_data_db(selectedCategory):
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT filename, path FROM files WHERE category = ?", (selectedCategory,))
    documentList = c.fetchall()
    conn.close()
    return documentList

def search_db(query):
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT filename, path, category FROM files WHERE content LIKE ?", ('%' + query + '%',))
    results = c.fetchall()
    conn.close()
    return results

def index_files(base_directory):
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.startswith("~$"):
                continue
            if file.endswith(".docx"):
                try:
                    doc = Document(os.path.join(root, file))
                    text = "\n".join([para.text for para in doc.paragraphs])
                    category = os.path.basename(root)
                    c.execute("INSERT INTO files (filename, content, path, category) VALUES (?, ?, ?, ?)",
                              (file, text, os.path.join(root, file), category))
                except Exception as e:
                    print(f"Error processing {file}: {e}")
            elif file.endswith(".xlsx"):
                try:
                    df = pd.read_excel(os.path.join(root, file))
                    text = df.to_string()
                    category = os.path.basename(root)
                    c.execute("INSERT INTO files (filename, content, path, category) VALUES (?, ?, ?, ?)",
                              (file, text, os.path.join(root, file), category))
                except Exception as e:
                    print(f"Error processing {file}: {e}")
    conn.commit()
    conn.close()
