import subprocess
import logging
from typing import Tuple, Dict, List
import platform

logger = logging.getLogger(__name__)


def run_command(command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """Execute a shell command and return (returncode, stdout, stderr)."""
    try:
        kwargs = {
            "shell": True,
            "capture_output": True,
            "text": True,
            "timeout": timeout,
        }
        if not platform.system().lower().startswith("win"):
            kwargs["executable"] = "/bin/bash"
        result = subprocess.run(command, **kwargs)
        logger.info("Executed command: %s", command)
        return result.returncode, result.stdout, result.stderr
    except Exception as exc:
        logger.exception("Error running command %s: %s", command, exc)
        return 1, "", str(exc)


def run_task(task: Dict) -> Tuple[int, str, str]:
    """Execute a single task dictionary."""
    ttype = task.get("type")
    if ttype == "create_file":
        path = task.get("path")
        try:
            open(path, "a").close()
            return 0, "", ""
        except Exception as exc:
            logger.exception("Failed create_file %s", exc)
            return 1, "", str(exc)
    if ttype == "write_to_file":
        path = task.get("path")
        content = task.get("content", "")
        try:
            with open(path, "w") as f:
                f.write(content)
            return 0, "", ""
        except Exception as exc:
            logger.exception("Failed write_to_file %s", exc)
            return 1, "", str(exc)
    if ttype == "command":
        return run_command(task.get("command", ""))
    return 1, "", f"Unknown task type: {ttype}"


def execute_plan(plan: Dict) -> List[Dict]:
    """Execute all tasks in the plan sequentially."""
    results = []
    for task in plan.get("tasks", []):
        code, out, err = run_task(task)
        results.append({
            "type": task.get("type"),
            "returncode": code,
            "stdout": out,
            "stderr": err,
        })
    return results
