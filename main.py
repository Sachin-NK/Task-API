from fastapi import FastAPI, HTTPException

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
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task
