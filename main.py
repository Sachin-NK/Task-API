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

SEED_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Go for a walk", "done": False},
]

tasks = [t.copy() for t in SEED_TASKS]

next_id = 4


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)


# ---------------------------------------------------------------------------
# General endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/",
    summary="API info",
    description="Returns the API name, version, and a list of available endpoint paths.",
)
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get(
    "/health",
    summary="Health check",
    description="Returns `{status: ok}` if the server is running. Useful for uptime monitoring.",
)
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/tasks",
    summary="List all tasks",
    description=(
        "Returns the full task list. "
        "Optionally filter by completion status with `?done=true/false` "
        "and/or search by keyword in the title with `?search=<term>`. "
        "Both query params can be combined."
    ),
)
def list_tasks(done: bool | None = None, search: str | None = None):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower()]
    return result


@app.get(
    "/tasks/{task_id}",
    summary="Get a task by ID",
    description="Returns a single task by its integer ID. Returns 404 if the task does not exist.",
)
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ---------------------------------------------------------------------------
# Create endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/tasks",
    summary="Create a task",
    description=(
        "Creates a new task with the provided title. "
        "`done` defaults to `false`. "
        "Returns 400 if the title is missing or blank. "
        "Returns 201 with the created task on success."
    ),
    status_code=201,
)
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

@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description=(
        "Partially updates a task. Both `title` and `done` are optional — "
        "only the fields you send will be changed. "
        "Returns 404 if the task does not exist. "
        "Returns 400 if a blank title is provided."
    ),
)
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

@app.delete(
    "/tasks/{task_id}",
    summary="Delete a task",
    description="Removes a task by ID. Returns 204 with no body on success. Returns 404 if not found.",
    status_code=204,
)
def delete_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)


# ---------------------------------------------------------------------------
# Stats endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/stats",
    summary="Task statistics",
    description="Returns a count of total tasks, completed tasks, and open (not done) tasks.",
)
def stats():
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done, "open": total - done}


# ---------------------------------------------------------------------------
# Reset endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/reset",
    summary="Reset tasks to seed data",
    description=(
        "Wipes all current tasks and restores the original 3 seed tasks. "
        "Resets the ID counter to 4. Useful for testing."
    ),
)
def reset():
    global tasks, next_id
    tasks = [t.copy() for t in SEED_TASKS]
    next_id = 4
    return tasks
