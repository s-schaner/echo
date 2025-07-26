import json
import logging
import re
import time
from typing import Dict, List

from llm_interpreter import interpret as llm_interpret

logger = logging.getLogger(__name__)


def _heuristic_tasks(text: str) -> List[Dict]:
    """Fallback parser to create simple tasks from text."""
    match = re.search(r"create a file named (\S+) and write '(.*)'", text, re.IGNORECASE)
    if match:
        path = match.group(1)
        content = match.group(2)
        return [
            {"type": "create_file", "path": path},
            {"type": "write_to_file", "path": path, "content": content},
        ]
    return [{"type": "command", "command": text}]


def create_plan(user_input: str) -> Dict:
    """Convert user input to a structured plan dictionary."""
    plan = llm_interpret(user_input)
    if not plan:
        tasks = _heuristic_tasks(user_input)
    else:
        tasks = plan.get("tasks", [])
    final_plan = {
        "capsule_id": f"capsule_{int(time.time())}",
        "description": user_input,
        "tasks": tasks,
        "trust_level": "low",
        "status": "pending",
        "created_by": "LLM_Local_Interpreter",
        "glyph_state": ["Alpha-0x7F", "Lambda-KN0W"],
    }
    logger.info("Created plan: %s", final_plan)
    return final_plan
