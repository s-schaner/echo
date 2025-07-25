import json
import os
import logging
from typing import Any, Dict

TMU_FILE = os.path.join('logs', 'tmu.json')
logger = logging.getLogger(__name__)


def append_log(entry: Dict[str, Any]) -> None:
    """Append an entry to the tmu.json log file."""
    os.makedirs(os.path.dirname(TMU_FILE), exist_ok=True)
    data = []
    if os.path.exists(TMU_FILE):
        try:
            with open(TMU_FILE, 'r') as f:
                data = json.load(f)
        except Exception:
            logger.exception('Failed to read tmu log')
            data = []
    data.append(entry)
    with open(TMU_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info('Appended entry to tmu log')
