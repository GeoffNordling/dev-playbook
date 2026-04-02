"""Pre-generation hook: validate template variables."""

import re
import sys

slug = "{{ cookiecutter.project_slug }}"
package = "{{ cookiecutter.package_name }}"

if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", slug):
    print(
        f"ERROR: project_slug '{slug}' is not valid. "
        "Use only lowercase letters, digits, and hyphens."
    )
    sys.exit(1)

if not re.match(r"^[a-z][a-z0-9_]*$", package):
    print(
        f"ERROR: package_name '{package}' is not valid. "
        "Use only lowercase letters, digits, and underscores (must start with a letter)."
    )
    sys.exit(1)
