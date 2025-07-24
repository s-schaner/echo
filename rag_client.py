import logging
import requests
import yaml

CONFIG_FILE = "config.yaml"
logger = logging.getLogger(__name__)

with open(CONFIG_FILE, "r") as f:
    CONFIG = yaml.safe_load(f)

BASE_URL = CONFIG.get("anythingllm_url", "http://localhost:3001")


def query_memory(text: str) -> dict:
    """Query AnythingLLM server for context or documents."""
    url = f"{BASE_URL}/query"
    try:
        resp = requests.post(url, json={"query": text}, timeout=10)
        resp.raise_for_status()
        logger.info("Queried AnythingLLM: %s", text)
        return resp.json()
    except Exception as exc:
        logger.exception("AnythingLLM request failed: %s", exc)
        return {}
