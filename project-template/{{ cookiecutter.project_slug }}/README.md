# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Prerequisites

- Python {{ cookiecutter.python_version }}+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Usage

```bash
uv run <command>
```

## Project Structure

```
.
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   └── skills/
├── tests/
{% if 'package' in cookiecutter.project_layout -%}
├── src/
│   └── {{ cookiecutter.package_name }}/
│       └── __init__.py
{% endif -%}
{% if 'scripts' in cookiecutter.project_layout -%}
├── scripts/
{% endif -%}
{% if 'notebooks' in cookiecutter.project_layout -%}
├── notebooks/
{% endif -%}
```
