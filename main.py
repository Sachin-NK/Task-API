from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

app = FastAPI(title="Task API", version="1.0")

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Go for a walk", "done": False},
]

next_id = 4


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)


# ---------------------------------------------------------------------------
# General endpoints
# ---------------------------------------------------------------------------

@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------

@app.get("/tasks", summary="List all tasks")
def list_tasks(done: bool | None = None):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    return result


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ---------------------------------------------------------------------------
# Create endpoint
# ---------------------------------------------------------------------------

@app.post("/tasks", summary="Create a task", status_code=201)
def create_task(body: TaskCreate):
    global next_id
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": body.title.strip(), "done": False}
    tasks.append(task)
    next_id += 1
    return task


# ---------------------------------------------------------------------------
# Update endpoint
# ---------------------------------------------------------------------------

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, body: TaskUpdate):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        task["title"] = body.title.strip()
    if body.done is not None:
        task["done"] = body.done
    return task


# ---------------------------------------------------------------------------
# Delete endpoint
# ---------------------------------------------------------------------------

@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
