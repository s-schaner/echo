import logging
import yaml

CONFIG_FILE = "config.yaml"
logger = logging.getLogger(__name__)


def load_allowlist() -> list:
    with open(CONFIG_FILE, "r") as f:
        data = yaml.safe_load(f)
    return data.get("allowlist", [])


ALLOWLIST = load_allowlist()


def is_allowed(command: str) -> bool:
    allowed = any(command.startswith(item) for item in ALLOWLIST)
    logger.info("Command '%s' allowed: %s", command, allowed)
    return allowed
