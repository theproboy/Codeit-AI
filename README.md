# Codeit-AI

A minimal browser-based **Python playground** with an AI assist: write code, run it,
and ask an LLM to **explain** what it does or **debug** an error — powered by
[Groq](https://groq.com) (Llama 3.3 70B).

No accounts, no database. A single-page frontend talks to a small Flask backend that
runs the code and forwards AI requests.

## What it does

| Action | Endpoint | Works without a key? |
|---|---|---|
| **Run** Python and see stdout/stderr | `POST /run` | ✅ yes |
| **Explain** what the code does | `POST /explain` | needs `GROQ_API_KEY` |
| **Debug** an error and suggest a fix | `POST /debug` | needs `GROQ_API_KEY` |

## How it works

```
Browser (index.html)  ──fetch──▶  Flask backend (app.py)
   code editor + buttons              ├─ /run     → subprocess python3 (5s timeout)
                                      ├─ /explain → Groq LLM
                                      └─ /debug   → Groq LLM
```

The editor sends your code to the backend. `/run` writes it to a temp file and executes
it with a timeout; `/explain` and `/debug` send it to Groq and return the model's answer.

## Run it locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # then paste a free Groq key from https://console.groq.com/keys
export GROQ_API_KEY=your_key  # (or use the .env value)
python app.py                 # serves on http://localhost:5000
```

**Frontend:** open `frontend/index.html` in your browser (or serve it with
`python -m http.server` from the `frontend/` folder).

`/run` works immediately; the Explain/Debug buttons light up once a `GROQ_API_KEY` is set.

## Security note (honest)

`/run` executes arbitrary Python **on the host machine**, protected only by a 5-second
timeout. That's fine for a local playground, but a public deployment would need real
sandboxing (Docker/nsjail/firecracker). This is a learning project, not a production
service — the limitation is intentional and called out rather than hidden.

## Tech

`Python` · `Flask` · `flask-cors` · `Groq (Llama 3.3 70B)` · vanilla HTML/JS frontend

## Possible next steps

- Sandbox `/run` in a Docker container.
- Swap the `<textarea>` for a real editor (Monaco/CodeMirror) with syntax highlighting.
- Support more languages by mapping file extensions to interpreters.
