"""Codeit-AI backend — run Python code and get AI help via Groq.

Three endpoints:
  POST /run      -> execute Python code in a subprocess, return stdout/stderr
  POST /explain  -> ask an LLM to explain what the code does
  POST /debug    -> ask an LLM to explain an error and suggest a fix

The AI endpoints use Groq (free tier). They only work if GROQ_API_KEY is set;
/run works without any key so the runner is usable on its own.
"""
import os
import re
import subprocess
import tempfile

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# CORS: only allow the local frontend by default, not every origin — otherwise any website
# open in the user's browser could drive-by call /run. Override with ALLOWED_ORIGINS
# (comma-separated). Serve the frontend over http (python -m http.server); a file:// page
# sends Origin "null" and is blocked unless you add it to ALLOWED_ORIGINS.
_allowed = os.environ.get("ALLOWED_ORIGINS")
if _allowed:
    CORS(app, origins=[o.strip() for o in _allowed.split(",")])
else:
    CORS(app, origins=re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"))

# Cap request bodies so a giant payload can't exhaust memory/disk.
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024  # 100 KB

MODEL = "llama-3.3-70b-versatile"
RUN_TIMEOUT = 5  # seconds a user's script is allowed to run


def sandbox_env() -> dict:
    """Environment for the user's subprocess, with secrets stripped out.

    subprocess inherits os.environ by default, which would hand the running script the
    server's GROQ_API_KEY — letting any snippet read and exfiltrate it. Drop anything that
    looks like a credential and keep only the harmless vars (PATH, HOME, LANG, ...).
    """
    blocked = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD", "CREDENTIAL", "API")
    return {k: v for k, v in os.environ.items()
            if not any(b in k.upper() for b in blocked)}


def ask_groq(system: str, user: str) -> str | None:
    """Send one chat request to Groq. Returns None if no API key is configured."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    from groq import Groq  # imported lazily so /run works without the package/key

    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


@app.post("/run")
def run_code():
    """Execute the posted Python code in a temp file and return its output.

    NOTE: this runs arbitrary code on the host with only a timeout — fine for a
    local playground, but a public deployment would need a real sandbox (Docker,
    nsjail, etc.). Called out honestly rather than hidden.
    """
    code = (request.json or {}).get("code", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400

    # Run inside a throwaway temp dir (auto-cleaned) used as the working directory, with a
    # secret-stripped environment so the snippet can't read the server's API key.
    with tempfile.TemporaryDirectory() as workdir:
        path = os.path.join(workdir, "snippet.py")
        with open(path, "w") as f:
            f.write(code)
        try:
            result = subprocess.run(
                ["python3", path], capture_output=True, text=True,
                timeout=RUN_TIMEOUT, env=sandbox_env(), cwd=workdir,
            )
            return jsonify({"output": result.stdout, "error": result.stderr})
        except subprocess.TimeoutExpired:
            return jsonify({"error": f"Execution timed out ({RUN_TIMEOUT}s limit)"})


@app.post("/explain")
def explain():
    code = (request.json or {}).get("code", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    out = ask_groq(
        "You are a concise programming tutor. Explain what the given code does, step by step.",
        code,
    )
    if out is None:
        return jsonify({"error": "GROQ_API_KEY not set — AI features are disabled."}), 503
    return jsonify({"explanation": out})


@app.post("/debug")
def debug():
    data = request.json or {}
    code, error = data.get("code", ""), data.get("error", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    out = ask_groq(
        "You are a debugging assistant. Given code and its error message, explain the bug "
        "in plain language and provide a corrected version.",
        f"Code:\n{code}\n\nError:\n{error}",
    )
    if out is None:
        return jsonify({"error": "GROQ_API_KEY not set — AI features are disabled."}), 503
    return jsonify({"fix": out})


if __name__ == "__main__":
    app.run(port=5000, debug=False)
