"""OFT traceability check via subprocess.

Delegates spec coverage tracing to the OpenFastTrace JAR. OFT verifies that
every Needs: declaration is satisfied by at least one Covers: link, and that
every Covers: link points to an existing item.

JAR: https://github.com/itsallcode/openfasttrace (v4.2.2)
"""

import shutil
import subprocess
from pathlib import Path


def resolve_oft_jar(jar_path: Path) -> Path:
    """Resolve and validate the OFT JAR path.

    Raises FileNotFoundError if the JAR does not exist at the given path.
    """
    if not jar_path.is_file():
        raise FileNotFoundError(
            f"OFT JAR not found: {jar_path}\n"
            "Download from https://github.com/itsallcode/openfasttrace/releases"
        )
    return jar_path


def require_java() -> str:
    """Return the path to the java executable.

    Raises RuntimeError if java is not found on PATH.
    """
    java = shutil.which("java")
    if java is None:
        raise RuntimeError(
            "java not found on PATH; required for OFT traceability checks.\n"
            "Install a JDK or JRE and ensure java is on your PATH."
        )
    return java


def run_oft_trace(jar_path: Path, specs_dir: Path) -> subprocess.CompletedProcess:
    """Run OFT trace on a spec directory.

    Raises RuntimeError if java is not on PATH.
    Raises FileNotFoundError if the JAR does not exist.
    Raises subprocess.CalledProcessError if OFT exits non-zero.
    """
    java = require_java()
    resolved_jar = resolve_oft_jar(jar_path)

    result = subprocess.run(
        [java, "-jar", str(resolved_jar), "trace", str(specs_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=output,
        )

    return result
