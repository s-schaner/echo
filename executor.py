import subprocess
import logging
from typing import Tuple
import platform

logger = logging.getLogger(__name__)


def run_command(command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """Execute command in subprocess and return (returncode, stdout, stderr)."""
    try:
        kwargs = {
            "shell": True,
            "capture_output": True,
            "text": True,
            "timeout": timeout,
        }
        # Use bash on POSIX systems and default shell on Windows
        if not platform.system().lower().startswith("win"):
            kwargs["executable"] = "/bin/bash"
        result = subprocess.run(command, **kwargs)
        logger.info("Executed command: %s", command)
        return result.returncode, result.stdout, result.stderr
    except Exception as exc:
        logger.exception("Error running command %s: %s", command, exc)
        return 1, "", str(exc)
