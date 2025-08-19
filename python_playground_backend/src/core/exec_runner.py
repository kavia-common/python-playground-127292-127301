from __future__ import annotations

import sys
import tempfile
import time
import subprocess
from typing import Dict

from src.core.config import get_settings

settings = get_settings()


# PUBLIC_INTERFACE
def run_code(code: str, timeout_s: int | None = None, memory_limit_mb: int | None = None) -> Dict[str, object]:
    """
    Execute Python code in a separate subprocess with time and memory limits.

    Security:
        This is a best-effort sandbox for educational purposes. It:
        - Uses Python isolated mode (-I) and disables site imports (-S).
        - Sets RLIMIT_CPU and RLIMIT_AS in the child process.
        - Blocks networking and common subprocess operations within the script.
        - Runs in an isolated temporary directory.

        True sandboxing (e.g., via containers, seccomp, or VM isolation) is recommended for production.

    Args:
        code: The Python code to execute.
        timeout_s: Wall-clock timeout seconds (defaults from settings).
        memory_limit_mb: Address space limit in MiB (defaults from settings).

    Returns:
        Dict with stdout, stderr, exit_code, duration_ms, and timed_out flags.
    """
    t0 = time.time()
    timeout_s = timeout_s or settings.EXEC_TIMEOUT_SECONDS
    mem_mb = memory_limit_mb or settings.EXEC_MEMORY_MB
    mem_bytes = mem_mb * 1024 * 1024

    # Child code that sets resource limits and then executes user code
    # We intentionally avoid reading from untrusted environment variables inside the child.
    prelude = f"""
import os, sys, resource, signal, tempfile
# Apply resource limits
resource.setrlimit(resource.RLIMIT_CPU, ({timeout_s}, {timeout_s}))
try:
    resource.setrlimit(resource.RLIMIT_AS, ({mem_bytes}, {mem_bytes}))
except (ValueError, AttributeError):
    # RLIMIT_AS may not be available on all platforms
    pass
resource.setrlimit(resource.RLIMIT_FSIZE, (10*1024*1024, 10*1024*1024))  # 10MB file size

# Replace working directory with a temp dir
td = tempfile.mkdtemp(prefix="pyplay-")
os.chdir(td)

# Block networking
import socket as _socket
def _block(*args, **kwargs): raise RuntimeError("Networking disabled in playground")
for name in ["socket", "create_connection", "gethostbyname", "getaddrinfo", "create_server"]:
    try: setattr(_socket, name, _block)
    except Exception: pass

# Block subprocess creation
import subprocess as _subprocess
for name in ["Popen", "call", "run", "check_call", "check_output"]:
    try: setattr(_subprocess, name, None)
    except Exception: pass

# Minimize environment
for k in list(os.environ.keys()):
    if k not in ["PYTHONIOENCODING"]:
        os.environ.pop(k, None)
"""

    # Compose final code for execution
    full_code = prelude + "\n# --- User Code Starts Here ---\n" + code + "\n"

    timed_out = False
    stdout = ""
    stderr = ""
    exit_code = 0

    # Use a temp directory to avoid any filesystem side-effects
    with tempfile.TemporaryDirectory(prefix="pyplay-root-") as tmpdir:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "-B", "-E", "-c", full_code],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout_s + 0.5,  # small cushion beyond CPU limit
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            exit_code = proc.returncode
        except subprocess.TimeoutExpired as ex:
            # Process exceeded wall-clock timeout
            timed_out = True
            stdout = ex.stdout or ""
            stderr = (ex.stderr or "") + "\nTimed out."
            exit_code = -9
        except Exception as ex:
            stderr = f"Runner error: {ex}"
            exit_code = -1

    duration_ms = int((time.time() - t0) * 1000)
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "timed_out": timed_out,
    }
