from contextlib import nullcontext as does_not_raise

import pytest

from cosmic_python_sandbox import events


@pytest.mark.parametrize(
    "msg, expected_result, expected_context",
    (
        pytest.param(
            {"priority_event": False, "invalid": ""},
            events.Event(priority_event=False),
            does_not_raise(),
        ),
        pytest.param(
            {"action": "copy", "src": "some_file.py", "dst": "some_other_file.py"},
            events.CopyFile(priority_event=False, src="some_file.py", dst="some_other_file.py"),
            does_not_raise(),
        ),
        pytest.param(
            {"action": "move", "src": "some_file.py", "dst": "renamed_file.py"},
            events.MoveFile(priority_event=False, src="some_file.py", dst="renamed_file.py"),
            does_not_raise(),
        ),
        pytest.param(
            {"action": "delete", "dst": "renamed_file.py"},
            events.DeleteFile(priority_event=False, dst="renamed_file.py"),
            does_not_raise(),
        ),
        pytest.param({"invalid": False, "msg": ""}, None, pytest.raises(ValueError)),
    ),
)
def test_parse_event(msg, expected_result, expected_context):
    with expected_context:
        assert events.parse_event(msg) == expected_result
