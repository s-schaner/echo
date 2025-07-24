from flask import Flask, request, jsonify
import logging
import yaml
from planner import create_plan
from validator import is_allowed
from executor import run_command

logging.basicConfig(
    filename="logs/agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

pending_plan = None


@app.route("/chat", methods=["POST"])
def chat():
    global pending_plan
    data = request.get_json() or {}
    text = data.get("message", "")
    approve = data.get("approve", False)

    if approve and pending_plan:
        plan = pending_plan
        pending_plan = None
        if not is_allowed(plan["command"]):
            logger.warning("Blocked command: %s", plan["command"])
            return jsonify({"error": "Command not allowed"})
        code, out, err = run_command(plan["command"])
        return jsonify({"returncode": code, "stdout": out, "stderr": err})

    # create new plan
    plan = create_plan(text)
    pending_plan = plan
    return jsonify({"plan": plan, "message": "Send {'approve': true} to execute"})


def main():
    port = CONFIG.get("port", 5000)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
