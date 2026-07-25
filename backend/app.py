"""Codeit-AI backend — run Python code and get AI help via Groq.

Three endpoints:
  POST /run      -> execute Python code in a subprocess, return stdout/stderr
  POST /explain  -> ask an LLM to explain what the code does
  POST /debug    -> ask an LLM to explain an error and suggest a fix

The AI endpoints use Groq (free tier). They only work if GROQ_API_KEY is set;
/run works without any key so the runner is usable on its own.
"""
import os
import subprocess
import tempfile

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL = "llama-3.3-70b-versatile"
RUN_TIMEOUT = 5  # seconds a user's script is allowed to run


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

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            ["python3", path], capture_output=True, text=True, timeout=RUN_TIMEOUT
        )
        return jsonify({"output": result.stdout, "error": result.stderr})
    except subprocess.TimeoutExpired:
        return jsonify({"error": f"Execution timed out ({RUN_TIMEOUT}s limit)"})
    finally:
        os.unlink(path)


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
