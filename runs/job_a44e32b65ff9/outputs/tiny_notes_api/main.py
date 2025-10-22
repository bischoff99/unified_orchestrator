```python
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

@app.post("/notes")
async def create_note(request: Request, response: Response):
    note = Note(**request.json())
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (note.title, note.content))
        conn.commit()
        response.status_code = 201
        return {"id": cursor.lastrowid}

@app.get("/notes")
async def get_notes(request: Request, response: Response):
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        notes = []
        for row in cursor.execute("SELECT * FROM notes"):
            notes.append({"id": row[0], "title": row[1], "content": row[2]})
    response.status_code = 200
    return {"notes": notes}
```
This code creates a FastAPI app with two endpoints: `/notes` for creating and retrieving notes. The `create_note` endpoint takes a JSON object with the title and content of the note, inserts it into the SQLite database, and returns the ID of the newly created note. The `get_notes` endpoint retrieves all the notes from the database and returns them as a JSON array.

Note that this code assumes that you have already created a SQLite database called "notes.db" with a table called "notes" that has the same schema as defined in the previous section.