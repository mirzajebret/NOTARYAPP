from flask import Blueprint, request, jsonify, render_template, send_file
from .models import get_document_counts, manage_todos_db, update_or_delete_todo_db, category_data_db, search_db, index_files
import os
import sqlite3

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    counts = get_document_counts()
    return render_template('index.html', counts=counts)

@main_bp.route('/category-documents', methods=['GET'])
def category_documents():
    selectedCategory = request.args.get('selectedCategory')
    return jsonify(category_data_db(selectedCategory))

@main_bp.route('/category-data', methods=['GET'])
def category_data():
    conn = sqlite3.connect('file_index.db')
    c = conn.cursor()
    c.execute("SELECT category, COUNT(DISTINCT filename) FROM files GROUP BY category")
    categoryData = dict(c.fetchall())
    conn.close()
    return jsonify(categoryData)


@main_bp.route('/todos', methods=['GET', 'POST'])
def manage_todos():
    return manage_todos_db(request)

@main_bp.route('/todos/<int:todo_id>', methods=['PUT', 'DELETE'])
def update_or_delete_todo(todo_id):
    return update_or_delete_todo_db(todo_id, request)

@main_bp.route('/download')
def download_file():
    file_path = request.args.get('path')
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)

@main_bp.route('/open_file', methods=['GET'])
def open_file():
    file_path = request.args.get('path')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    return jsonify(search_db(query))
