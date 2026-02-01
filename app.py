from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow React frontend to make requests

DB_NAME = "todos.db"

# -----------------------
# Helper function: DB connection
# -----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # rows ko dictionary ki tarah access karne ke liye
    return conn

# -----------------------
# Initialize database (if not exists)
# -----------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo TEXT NOT NULL,
            isCompleted BOOLEAN NOT NULL CHECK (isCompleted IN (0, 1))
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# GET all todos
# -----------------------
@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    # Convert each row to dictionary
    return jsonify([dict(todo) for todo in todos])

# -----------------------
# POST new todo
# -----------------------
@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    todo_text = data.get("todo", "").strip()
    if not todo_text:
        return jsonify({"error": "Todo text cannot be empty"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO todos (todo, isCompleted) VALUES (?, ?)",
        (todo_text, False)
    )
    conn.commit()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return jsonify([dict(todo) for todo in todos])

# -----------------------
# PUT update todo (edit or checkbox toggle)
# -----------------------
@app.route("/todos/<int:id>", methods=["PUT"])
def update_todo(id):
    data = request.get_json()
    todo_text = data.get("todo", "").strip()
    isCompleted = data.get("isCompleted", False)

    conn = get_db_connection()
    conn.execute(
        "UPDATE todos SET todo = ?, isCompleted = ? WHERE id = ?",
        (todo_text, bool(isCompleted), id)
    )
    conn.commit()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return jsonify([dict(todo) for todo in todos])

# -----------------------
# DELETE todo
# -----------------------
@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (id,))
    conn.commit()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return jsonify([dict(todo) for todo in todos])

# -----------------------
# Run server
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
