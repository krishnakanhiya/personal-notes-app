import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Absolute path resolution ensures SQLite writes reliably in Render's environment
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "notes.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Executed at module import so Gunicorn initializes the schema before serving requests
init_db()

# --- Page Routes ---

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/notes')
def notes_page():
    return render_template('notes.html')

@app.route('/edit/<int:note_id>')
def edit_note_page(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    if note is None:
        return redirect(url_for('notes_page'))
    return render_template('edit_note.html', note=note)

# --- REST API Endpoints ---

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes ORDER BY id DESC').fetchall()
    conn.close()
    notes_list = [dict(note) for note in notes]
    return jsonify(notes_list), 200

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400

    title = data.get('title').strip()
    content = data.get('content').strip()
    url = data.get('url', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notes (title, content, url) VALUES (?, ?, ?)',
        (title, content, url)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': new_id, 'message': 'Note created successfully'}), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_single_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return jsonify(dict(note)), 200

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400

    title = data.get('title').strip()
    content = data.get('content').strip()
    url = data.get('url', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE notes SET title = ?, content = ?, url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, content, url, note_id)
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

    if updated_rows == 0:
        return jsonify({'error': 'Note not found'}), 404

    return jsonify({'message': 'Note updated successfully'}), 200

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()

    if deleted_rows == 0:
        return jsonify({'error': 'Note not found'}), 404

    return jsonify({'message': 'Note deleted successfully'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)