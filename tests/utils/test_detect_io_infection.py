from pathlib import Path

import pytest

from cosmic_python_sandbox.utils.detect_io_infection import find_io_infected_funcs

REPO_ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize(
    ("inp_root", "expected_result"),
    [
        pytest.param(
            REPO_ROOT.joinpath("mock_data"),
            [
                {
                    "module": "basic_funcs.py",
                    "func": "get_file_io_inf",
                    "line_no": 2,
                    "calls": "open",
                    "io_call": True,
                    "io_func": True,
                    "infected_by": "",
                },
                {
                    "module": "basic_funcs.py",
                    "func": "process_data_io_inf",
                    "line_no": 7,
                    "calls": "get_file_io_inf",
                    "io_call": True,
                    "io_func": True,
                    "infected_by": "get_file_io_inf",
                },
            ],
        ),
    ],
)
def test_find_io_infected_funcs(inp_root, expected_result):
    assert find_io_infected_funcs(inp_root).to_dict("records") == expected_result
