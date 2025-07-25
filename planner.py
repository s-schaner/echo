import json
import logging

logger = logging.getLogger(__name__)


def create_plan(user_input: str) -> dict:
    """Convert user input to a plan dictionary.

    This is a placeholder implementation. In a real system, this would call
    an LLM (e.g. LM Studio) to parse intent and return a structured plan.
    """
    try:
        data = json.loads(user_input)
        if isinstance(data, dict) and "command" in data:
            command = data["command"]
        else:
            command = user_input
    except json.JSONDecodeError:
        command = user_input

    plan = {
        "task": "user_request",
        "command": command,
        "requires_approval": True,
    }

    logger.info("Created plan: %s", plan)
    return plan
