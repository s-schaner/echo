import logging
import requests
import yaml

CONFIG_FILE = "config.yaml"
logger = logging.getLogger(__name__)

def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def query_memory(text: str) -> dict:
    """Query AnythingLLM server for context or documents."""
    cfg = load_config()
    base_url = cfg.get("anythingllm_url", "http://localhost:3001")
    token = cfg.get("anythingllm_token")
    url = f"{base_url}/query"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(url, json={"query": text}, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info("Queried AnythingLLM: %s", text)
        return resp.json()
    except Exception as exc:
        logger.exception("AnythingLLM request failed: %s", exc)
        return {}
