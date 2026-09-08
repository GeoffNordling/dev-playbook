import pytest

from dev_playbook.cloa_viewer import cli


def test_main_returns_zero() -> None:
    assert cli.main([]) == 0


def test_port_defaults_to_8765() -> None:
    assert cli.parse_args([]).port == 8765


def test_port_flag_parses_to_an_integer() -> None:
    assert cli.parse_args(["--port", "9000"]).port == 9000


def test_checkout_arguments_collect_into_a_list() -> None:
    assert cli.parse_args(["/a", "/b"]).checkout == ["/a", "/b"]


def test_no_checkout_argument_is_an_empty_list() -> None:
    assert cli.parse_args([]).checkout == []


def test_unknown_flag_exits() -> None:
    with pytest.raises(SystemExit):
        cli.parse_args(["--nope"])
