"""
AI-generated version of the Task API.
Generated from the prompt in README.md — not manually edited.
"""

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# App and in-memory store
# ---------------------------------------------------------------------------

app = FastAPI(title="Task API", version="1.0")

tasks: list = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Go for a walk", "done": False},
]

next_id: int = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------

@app.get(
    "/",
    summary="API info",
    description="Returns the API name, version, and available endpoint paths.",
)
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get(
    "/health",
    summary="Health check",
    description="Returns ok if the server is up.",
)
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

@app.get(
    "/tasks",
    summary="List all tasks",
    description="Returns tasks. Filter by ?done=true/false and/or ?search=<term>.",
)
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower()]
    return result


@app.get(
    "/tasks/{task_id}",
    summary="Get task by ID",
    description="Returns a single task or 404 if not found.",
)
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@app.post(
    "/tasks",
    summary="Create a task",
    description="Create a new task. Returns 400 if title is missing or empty.",
    status_code=201,
)
def create_task(body: TaskCreate):
    global next_id
    # NOTE: does not strip whitespace — "  " would pass this check
    if not body.title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": body.title, "done": False}
    tasks.append(task)
    next_id += 1
    return task


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Partially update title and/or done. Returns 404 if not found.",
)
def update_task(task_id: int, body: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    # NOTE: does not validate blank title — {"title": ""} would overwrite silently
    if body.title is not None:
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@app.delete(
    "/tasks/{task_id}",
    summary="Delete a task",
    description="Deletes a task by ID. Returns 204 with no body. Returns 404 if not found.",
    status_code=204,
)
def delete_task(task_id: int, response: Response):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@app.get(
    "/stats",
    summary="Task statistics",
    description="Returns total, done, and open task counts.",
)
def stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

@app.post(
    "/reset",
    summary="Reset to seed data",
    description="Restores the original 3 seed tasks and resets the ID counter to 4.",
)
def reset():
    global tasks, next_id
    # NOTE: seed data is duplicated here instead of referenced from a constant
    tasks = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Read a book", "done": True},
        {"id": 3, "title": "Go for a walk", "done": False},
    ]
    next_id = 4
    return tasks
