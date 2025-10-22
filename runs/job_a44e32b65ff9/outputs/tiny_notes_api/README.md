
Overview
========

This is a FastAPI notes app with SQLite database that allows users to store and retrieve notes using two endpoints (POST /notes, GET /notes). The app will have a web-based frontend built using HTML, CSS, and JavaScript, and a backend server built using Python 3.x and FastAPI. The backend server will communicate with the SQLite database to store and retrieve data.

Quickstart
==========

To get started with this project, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Start the backend server by running `uvicorn main:app --reload`.
4. Open a web browser and navigate to `http://localhost:8000/docs` to view the API documentation.
5. Use the API endpoints to create and retrieve notes.

Setup Instructions
==================

To set up this project, follow these steps:

1. Clone this repository to your local machine.
2. Install Python 3.x and FastAPI.
3. Create a new SQLite database file called `notes.db`.
4. Run the following SQL commands to create the `notes` table:
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
5. Create a new Python file called `main.py` and add the following code:
```python
from fastapi import FastAPI, Request, Response
from sqlite3 import connect

app = FastAPI()

@app.get("/notes")
async def get_notes(request: Request):
    conn = connect("notes.db")
    cursor = conn.cursor()
    notes = cursor.execute("SELECT * FROM notes").fetchall()
    return Response(json.dumps(notes), media_type="application/json")

@app.post("/notes")
async def create_note(request: Request):
    data = await request.json()
    conn = connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, content) VALUES (:title, :content)", {"title": data["title"], "content": data["content"]})
    return Response(status_code=201)
```
6. Start the backend server by running `uvicorn main:app --reload`.
7. Open a web browser and navigate to `http://localhost:8000/docs` to view the API documentation.

API Documentation
==================

This section provides detailed information about the API endpoints available in this project.

### GET /notes

Retrieve all notes.

**Request**

* No request body is required.

**Response**

* `200 OK` with a JSON array of objects, each representing a note.
* Each object will have the following fields:
	+ `id`: The unique identifier for the note.
	+ `title`: The title of the note.
	+ `content`: The content of the note.
	+ `created_at`: The timestamp when the note was created.
	+ `updated_at`: The timestamp when the note was last updated.

### POST /notes

Create a new note.

**Request**

* A JSON object with the following fields:
	+ `title`: The title of the note.
	+ `content`: The content of the note.

**Response**

* `201 Created` if the note was created successfully.
* `400 Bad Request` if the request body is invalid or missing required fields.

Conclusion
==========

This system architecture provides a complete solution for creating a FastAPI notes app with SQLite database. The app will allow users to create and retrieve notes using two endpoints. The backend server will handle all the business logic of the app, while the frontend will provide a user-friendly interface for interacting with the app.