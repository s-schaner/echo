import logging
import requests
import yaml

CONFIG_FILE = "config.yaml"
logger = logging.getLogger(__name__)

with open(CONFIG_FILE, "r") as f:
    CONFIG = yaml.safe_load(f)

BASE_URL = CONFIG.get("n8n_url", "http://localhost:5678")


def trigger_workflow(workflow: str, data: dict | None = None) -> bool:
    """Trigger an N8N workflow by name."""
    url = f"{BASE_URL}/{workflow}"
    try:
        resp = requests.post(url, json=data or {}, timeout=10)
        resp.raise_for_status()
        logger.info("Triggered workflow %s", workflow)
        return True
    except Exception as exc:
        logger.exception("Failed to trigger workflow %s: %s", workflow, exc)
        return False
