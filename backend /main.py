# Backend entry point
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            filename = f.name

        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=2
        )
        return jsonify({
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"})

if __name__ == "__main__":
    app.run(debug=True)
