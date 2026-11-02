import io
import os

import pytest

from android_translator import create_parser
from android_translator_gui import build_argv, run_command
from commands import html_export, html_import, strings_export, strings_import


@pytest.mark.parametrize(
    "command, handler, flag_attr",
    [
        ("strings export", strings_export.execute, None),
        ("strings import", strings_import.execute, None),
        ("html export", html_export.execute, "remove_html_tags"),
        ("html import", html_import.execute, "plain_text_to_html"),
    ],
)
def test_build_argv_is_accepted_by_the_cli(command, handler, flag_attr):
    args = create_parser().parse_args(build_argv(command, "/p/App", "/x/out", "it", True))

    assert args.func is handler
    assert args.output_dir.as_posix().endswith("/x/out")
    if command.startswith("strings"):
        assert args.android_root.name == "App"
        assert args.default_language == "it"
    else:
        assert args.html_path.name == "App"
        assert getattr(args, flag_attr) is True


def test_build_argv_makes_relative_paths_absolute():
    argv = build_argv("html export", "-odd", "out")

    assert argv[2] == os.path.abspath("-odd")
    assert argv[3] == f"--output-dir={os.path.abspath('out')}"


def test_flag_is_left_out_when_unchecked():
    assert "--remove-html-tags" not in build_argv("html export", "/p", "/o")


def test_run_command_exports_a_project(tmp_path):
    values = tmp_path / "App" / "app" / "src" / "main" / "res" / "values"
    values.mkdir(parents=True)
    (values / "strings.xml").write_text(
        '<resources><string name="hello">Hello</string></resources>', encoding="utf-8"
    )
    log = io.StringIO()

    run_command(build_argv("strings export", tmp_path / "App", tmp_path / "xl", "en"), log)

    assert (tmp_path / "xl" / "App" / "app" / "app.xlsx").exists(), log.getvalue()


def test_run_command_logs_errors_instead_of_raising(tmp_path):
    log = io.StringIO()

    run_command(build_argv("strings export", tmp_path / "missing", tmp_path / "xl", "en"), log)

    assert "does not exist" in log.getvalue()
