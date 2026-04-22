"""Fixture module for test_interface.py — defines symbols to be introspected."""

from __future__ import annotations

import pathlib


def parse_session(path: pathlib.Path) -> str:
    return str(path)


def with_default(value: int = 5) -> int:
    return value


def with_optional(value: int | None = None) -> int:
    return value or 0


def with_list(items: list[int]) -> int:
    return sum(items)


def with_kwonly(*, flag: bool) -> bool:
    return flag


def with_var_args(*args: int, **kwargs: str) -> None:
    return None


class Session:
    def __init__(self, name: str) -> None:
        self.name = name

    def run(self) -> None:
        return None
