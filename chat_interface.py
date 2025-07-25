from flask import Flask, request, jsonify, render_template
from typing import List, Dict
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

CONFIG_FILE = "config.yaml"


def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(cfg, f)


CONFIG = load_config()

STATUS = {
    "lmstudio": False,
    "anythingllm": False,
    "n8n": False,
}

EVENTS: list[str] = []
LM_MESSAGES: List[Dict[str, str]] = []


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


def call_lmstudio(messages: List[Dict[str, str]]) -> str:
    """Send chat messages to LM Studio and return the assistant reply."""
    url = CONFIG.get("lmstudio_url", "")
    if not url:
        raise RuntimeError("LM Studio URL not configured")
    if not url.endswith("/v1/chat/completions"):
        url = url.rstrip("/") + "/v1/chat/completions"
    headers = {}
    token = CONFIG.get("lmstudio_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = {"model": "local", "messages": messages}
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return content


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


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Get or update server configuration."""
    global CONFIG
    if request.method == "POST":
        data = request.get_json() or {}
        CONFIG.update({
            "lmstudio_url": data.get("lmstudio_url", CONFIG.get("lmstudio_url")),
            "anythingllm_url": data.get("anythingllm_url", CONFIG.get("anythingllm_url")),
            "n8n_url": data.get("n8n_url", CONFIG.get("n8n_url")),
            "lmstudio_token": data.get("lmstudio_token", CONFIG.get("lmstudio_token")),
            "anythingllm_token": data.get("anythingllm_token", CONFIG.get("anythingllm_token")),
            "n8n_token": data.get("n8n_token", CONFIG.get("n8n_token")),
        })
        save_config(CONFIG)
    return jsonify({
        "lmstudio_url": CONFIG.get("lmstudio_url"),
        "anythingllm_url": CONFIG.get("anythingllm_url"),
        "n8n_url": CONFIG.get("n8n_url"),
        "lmstudio_token": CONFIG.get("lmstudio_token"),
        "anythingllm_token": CONFIG.get("anythingllm_token"),
        "n8n_token": CONFIG.get("n8n_token"),
    })


@app.route("/lmchat", methods=["GET", "POST"])
def lmchat():
    """Interactive chat endpoint and page for LM Studio conversations."""
    if request.method == "GET":
        return render_template("lmchat.html")
    data = request.get_json() or {}
    text = data.get("message", "")
    if not text:
        return jsonify({"error": "No message"})
    LM_MESSAGES.append({"role": "user", "content": text})
    try:
        reply = call_lmstudio(LM_MESSAGES)
        LM_MESSAGES.append({"role": "assistant", "content": reply})
        return jsonify({"response": reply})
    except Exception as exc:
        logger.exception("LM Studio chat failed: %s", exc)
        return jsonify({"error": str(exc)})


@app.route("/chat", methods=["POST"])
def chat():
    global pending_plan
    data = request.get_json() or {}
    text = data.get("message", "")
    mode = data.get("mode", "chat")
    approve = data.get("approve", False)

    if approve and pending_plan:
        plan = pending_plan
        pending_plan = None
        if not is_allowed(plan["command"]):
            logger.warning("Blocked command: %s", plan["command"])
            return jsonify({"error": "Command not allowed"})
        code, out, err = run_command(plan["command"])
        return jsonify({"returncode": code, "stdout": out, "stderr": err})

    if mode == "chat":
        plan = create_plan(text)
        return jsonify({"response": f"Proposed plan: {plan}"})

    # mode == execute: create plan and ask for approval
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
