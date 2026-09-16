# Task API

A simple in-memory to-do list API built with FastAPI. Supports full CRUD operations, optional filtering and search, task statistics, and a reset endpoint. Data lives only in memory - restarting the server resets everything back to the 3 seed tasks, which is intentional for this assignment.

---

## Running the API

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---

## Endpoints

| Method | Path | Success code | Description |
|--------|------|-------------|-------------|
| GET | `/` | 200 | API name, version, and available paths |
| GET | `/health` | 200 | Returns `{"status": "ok"}` |
| GET | `/tasks` | 200 | List all tasks. Supports `?done=true/false` and `?search=<term>` |
| GET | `/tasks/{id}` | 200 / 404 | Get a single task by ID |
| POST | `/tasks` | 201 / 400 | Create a task. Body: `{"title": "..."}`. Blank title → 400 |
| PUT | `/tasks/{id}` | 200 / 400 / 404 | Partial update. Send `title`, `done`, or both |
| DELETE | `/tasks/{id}` | 204 / 404 | Delete a task, returns no body |
| GET | `/stats` | 200 | `{"total": n, "done": n, "open": n}` |
| POST | `/reset` | 200 | Restore the 3 seed tasks and reset the ID counter |

---

## Example curl session

```
$ curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'

HTTP/1.1 201 Created
content-type: application/json
...

{"id":4,"title":"Buy milk","done":false}
```

---

## Swagger UI

Open [http://localhost:8000/docs](http://localhost:8000/docs) after starting the server.
FastAPI generates the interactive docs automatically — no extra setup needed.

## What happens when you restart the server?

Restarting `uvicorn` clears all tasks and restores the 3 seed tasks. This is because data is stored in a plain Python list in memory — there is no database or file. Every new process starts fresh, which is exactly the intended behaviour for this assignment.

---

## AI vs me

### The prompt I gave

> Build a to-do list REST API in Python using FastAPI.
> Use in-memory storage only — no database, no files. Data loss on restart is fine.
> 
> Endpoints required:
> - GET /           → {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}
> - GET /health     → {"status": "ok"}
> - GET /tasks      → list all tasks; support ?done=true/false filter and ?search=<term> (case-insensitive title match); both can combine
> - GET /tasks/{id} → return one task or 404 {"detail": "Task <id> not found"}
> - POST /tasks     → body {"title": str}; 201 on success; 400 if title is missing or blank after strip
> - PUT /tasks/{id} → partial update, body {"title": str | null, "done": bool | null}; 200 on success; 400 for blank title; 404 if not found
> - DELETE /tasks/{id} → 204 no body on success; 404 if not found
> - GET /stats      → {"total": n, "done": n, "open": n}
> - POST /reset     → restore original 3 seed tasks, reset id counter to 4, return the seed list
> 
> Seed data: id 1 "Buy groceries" done=false, id 2 "Read a book" done=true, id 3 "Go for a walk" done=false.
> next_id starts at 4.
> 
> Validation: POST and PUT both return 400 if title is present but empty after .strip().
> PUT with no title field at all should leave the title unchanged.
> 
> Every route must have a summary= and description= for Swagger UI at /docs.
> Single file: main.py. FastAPI + Uvicorn only.

### What the AI did better

- The AI generated the entire file in one shot with no iteration, while I built it incrementally over several commits.
- Its docstring-style descriptions were slightly more concise than mine.
- It used a `Response` parameter on the DELETE route to explicitly set the 204 status, which is a cleaner FastAPI pattern than relying solely on `status_code=204` in the decorator.

### What the AI got wrong or skipped

- The AI reset endpoint returned a new list literal instead of copying from a shared `SEED_TASKS` constant, meaning the seed was duplicated in two places - a maintenance hazard.
- It did not strip whitespace from the title in the POST handler, so `{"title": "  "}` would pass validation and create a blank task.
- The PUT route did not validate a blank title when the field was explicitly provided, missing the 400 requirement for `{"title": ""}`.

### What my prompt forgot to specify

I did not tell the AI where to place the models (before or after `app = FastAPI()`), so its ordering differed slightly from mine. One extra sentence - "define Pydantic models before instantiating the app" — would have closed that gap.

### Rematch (improved prompt run)

Added explicit instructions about model ordering and whitespace stripping; the regenerated version matched my implementation on all three points above.
