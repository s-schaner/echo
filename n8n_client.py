import logging
import requests
import yaml

CONFIG_FILE = "config.yaml"
logger = logging.getLogger(__name__)

def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def trigger_workflow(workflow: str, data: dict | None = None) -> bool:
    """Trigger an N8N workflow by name."""
    cfg = load_config()
    base_url = cfg.get("n8n_url", "http://localhost:5678")
    token = cfg.get("n8n_token")
    url = f"{base_url}/{workflow}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(url, json=data or {}, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info("Triggered workflow %s", workflow)
        return True
    except Exception as exc:
        logger.exception("Failed to trigger workflow %s: %s", workflow, exc)
        return False
