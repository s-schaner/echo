from flask import Flask, request, jsonify, render_template
import logging
import threading
import time
import requests
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

app = Flask(__name__, static_folder="static", template_folder="templates")

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

STATUS = {
    "lmstudio": False,
    "anythingllm": False,
    "n8n": False,
}

EVENTS: list[str] = []


def ping_service(name: str, url: str) -> bool:
    """Return True if service responds, False otherwise."""
    try:
        requests.get(url, timeout=3)
        return True
    except Exception:
        return False


def check_services() -> None:
    """Background thread to poll service availability."""
    while True:
        for name, key in {
            "lmstudio": "lmstudio_url",
            "anythingllm": "anythingllm_url",
            "n8n": "n8n_url",
        }.items():
            url = CONFIG.get(key)
            if not url:
                continue
            available = ping_service(name, url)
            if STATUS.get(name) != available:
                STATUS[name] = available
                msg = (
                    f"connection to {name} restored"
                    if available
                    else f"connection to {name} down"
                )
                logger.info(msg)
                EVENTS.append(msg)
        time.sleep(10)

pending_plan = None


@app.route("/")
def index():
    """Serve chat UI with motif skin."""
    return render_template("index.html")


@app.route("/system")
def system_page():
    """Serve system status page."""
    return render_template("status.html")


@app.route("/status")
def status():
    """Return JSON status of external services."""
    return jsonify(STATUS)


@app.route("/events")
def events():
    """Return and clear recent event messages."""
    global EVENTS
    msgs = EVENTS.copy()
    EVENTS.clear()
    return jsonify(msgs)


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
    # start background service checker
    thread = threading.Thread(target=check_services, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
