from flask import Flask, request, jsonify, render_template
from typing import List, Dict
import logging
import threading
import time
import platform
import os
import requests
import yaml
from planner import create_plan
from validator import is_allowed
import validator
from executor import execute_plan
from task_logger import append_log

logging.basicConfig(
    filename="logs/agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")

CONFIG_FILE = "config.yaml"


def default_allowlist() -> list:
    """Return a basic set of commands based on the host OS."""
    if platform.system().lower().startswith("win"):
        return [
            "echo",
            "dir",
            "cd",
            "mkdir",
            "rmdir",
            "type",
            "copy",
            "move",
            "del",
            "cls",
        ]
    return [
        "echo",
        "ls",
        "pwd",
        "whoami",
        "date",
        "uptime",
        "cd",
        "mkdir",
        "rmdir",
        "touch",
        "cat",
        "cp",
        "mv",
        "rm",
        "head",
        "tail",
        "grep",
        "find",
    ]


def load_config() -> dict:
    """Load configuration file and ensure new server list keys exist."""
    changed = False
    if not os.path.exists(CONFIG_FILE):
        cfg = {"port": 5000, "allowlist": default_allowlist()}
        changed = True
        data = cfg
    else:
        with open(CONFIG_FILE, "r") as f:
            data = yaml.safe_load(f) or {}

    if not data.get("allowlist"):
        data["allowlist"] = default_allowlist()
        changed = True

    defaults = {
        "lmstudio": "http://localhost:1234",
        "anythingllm": "http://localhost:3001",
        "n8n": "http://localhost:5678",
    }
    for svc, url in defaults.items():
        list_key = f"{svc}_servers"
        url_key = f"{svc}_url"
        tok_key = f"{svc}_token"
        if list_key not in data:
            # initialize list from existing url/token if present
            entry = {
                "url": data.get(url_key, url),
                "token": data.get(tok_key, ""),
            }
            data[list_key] = [entry]
            changed = True
        if url_key not in data and data.get(list_key):
            data[url_key] = data[list_key][0].get("url", "")
            changed = True
        if tok_key not in data and data.get(list_key):
            data[tok_key] = data[list_key][0].get("token", "")
            changed = True

    if changed:
        save_config(data)
    return data


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(cfg, f)


CONFIG = load_config()
validator.ALLOWLIST = CONFIG.get("allowlist", [])

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
        if name == "lmstudio":
            url = url.rstrip("/") + "/v1/models"
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


@app.route("/allowlist", methods=["GET", "POST"])
def allowlist_endpoint():
    """Get or append allowed commands."""
    global CONFIG
    if request.method == "POST":
        data = request.get_json() or {}
        cmd = data.get("command", "").strip()
        if cmd:
            CONFIG.setdefault("allowlist", [])
            if cmd not in CONFIG["allowlist"]:
                CONFIG["allowlist"].append(cmd)
                validator.ALLOWLIST = CONFIG["allowlist"]
                save_config(CONFIG)
    return jsonify(CONFIG.get("allowlist", []))


@app.route("/commands")
def commands_page():
    """Display allowed commands and form to add more."""
    return render_template("commands.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Get or update server configuration."""
    global CONFIG
    if request.method == "POST":
        data = request.get_json() or {}
        for svc in ["lmstudio", "anythingllm", "n8n"]:
            url_key = f"{svc}_url"
            tok_key = f"{svc}_token"
            list_key = f"{svc}_servers"
            if list_key in data:
                CONFIG[list_key] = data[list_key]
            if url_key in data:
                CONFIG[url_key] = data[url_key]
            if tok_key in data:
                CONFIG[tok_key] = data[tok_key]
        save_config(CONFIG)
        validator.ALLOWLIST = CONFIG.get("allowlist", validator.ALLOWLIST)

    response = {
        "lmstudio_url": CONFIG.get("lmstudio_url"),
        "lmstudio_token": CONFIG.get("lmstudio_token"),
        "lmstudio_servers": CONFIG.get("lmstudio_servers", []),
        "anythingllm_url": CONFIG.get("anythingllm_url"),
        "anythingllm_token": CONFIG.get("anythingllm_token"),
        "anythingllm_servers": CONFIG.get("anythingllm_servers", []),
        "n8n_url": CONFIG.get("n8n_url"),
        "n8n_token": CONFIG.get("n8n_token"),
        "n8n_servers": CONFIG.get("n8n_servers", []),
    }
    return jsonify(response)


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
        for task in plan.get("tasks", []):
            if task.get("type") == "command" and not is_allowed(task.get("command", "")):
                logger.warning("Blocked command: %s", task.get("command"))
                return jsonify({"error": f"Command not allowed: {task.get('command')}"})
        results = execute_plan(plan)
        append_log({"plan": plan, "results": results})
        return jsonify({"results": results})

    if mode == "chat":
        LM_MESSAGES.append({"role": "user", "content": text})
        try:
            reply = call_lmstudio(LM_MESSAGES)
            LM_MESSAGES.append({"role": "assistant", "content": reply})
            return jsonify({"response": reply})
        except Exception as exc:
            logger.exception("Chat failed: %s", exc)
            return jsonify({"error": str(exc)})

    # mode == execute: create plan and ask for approval
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
