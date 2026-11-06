import os
import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_NAME = "notes.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                url TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notes)")
        columns = [col[1] for col in cursor.fetchall()]
        if "url" not in columns:
            cursor.execute("ALTER TABLE notes ADD COLUMN url TEXT")
        conn.commit()


# Page 1: Welcome Screen
@app.route("/")
def welcome_page():
    if os.path.exists(os.path.join(app.template_folder, "welcome.html")):
        return render_template("welcome.html")
    return render_template("index.html")


# Page 2: Dashboard (All Notes)
@app.route("/notes")
@app.route("/notes.html")
def notes_page():
    return render_template("notes.html")


# Page 3: Dedicated Note Editor Page
@app.route("/note/<int:note_id>")
def note_editor_page(note_id):
    return render_template("edit_note.html", note_id=note_id)


# API: Get All Notes
@app.route("/api/notes", methods=["GET"])
def get_notes():
    with get_db_connection() as conn:
        notes = conn.execute(
            "SELECT id, title, content, url, updated_at FROM notes ORDER BY id DESC"
        ).fetchall()
        return jsonify([dict(note) for note in notes]), 200


# API: Get Single Note by ID
@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_single_note(note_id):
    with get_db_connection() as conn:
        note = conn.execute(
            "SELECT id, title, content, url, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        if not note:
            return jsonify({"error": "Note not found"}), 404
        return jsonify(dict(note)), 200


# API: Create Note
@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("content"):
        return jsonify({"error": "Title and content required"}), 400

    title = data["title"].strip()
    content = data["content"].strip()
    url = data.get("url", "").strip() or None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, url, updated_at) VALUES (?, ?, ?, datetime('now', 'localtime'))",
            (title, content, url),
        )
        conn.commit()
        new_note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return jsonify(dict(new_note)), 201


# API: Update Note
@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    url = data.get("url", "").strip() or None

    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notes SET title=?, content=?, url=?, updated_at=datetime('now', 'localtime') WHERE id=?",
            (title, content, url, note_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404
        updated = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()

    return jsonify(dict(updated)), 200


# API: Delete Note
@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404
    return jsonify({"message": "Deleted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)