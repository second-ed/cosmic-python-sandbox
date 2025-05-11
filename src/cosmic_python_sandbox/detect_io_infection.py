import ast
import glob
import os

import numpy as np
import pandas as pd


def read_file(path: str) -> str:
    with open(path, "r") as f:
        data = f.read()
    return data


def read_pkg_files(root: str, exclude: list[str]) -> dict[str, str]:
    paths = glob.glob(f"{root}/**/**.py", recursive=True)
    return {path: read_file(path) for path in paths if path not in exclude}


def get_nodes_from_body(
    root_node,
    ast_types,
):
    nodes = []
    for node in root_node.body:
        nodes += [n for n in ast.walk(node) if isinstance(n, tuple(ast_types))]
    return nodes


def get_funcs(node):
    return get_nodes_from_body(node, [ast.FunctionDef])


def get_calls(node):
    return get_nodes_from_body(node, [ast.Call])


def get_call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def propagate_io_infection(calls_df: pd.DataFrame) -> pd.DataFrame:
    calls_df = calls_df.copy()
    infected = set(calls_df[calls_df["io_call"]]["func"])
    infected_by = {}
    changed = True
    while changed:
        changed = False
        callers = calls_df[
            calls_df["calls"].isin(infected) & ~calls_df["func"].isin(infected)
        ].to_dict("records")

        for row in callers:
            func = row["func"]
            caller = row["calls"]
            infected.add(func)
            infected_by[func] = caller
            changed = True

    calls_df["io_func"] = calls_df["func"].isin(infected)
    calls_df["infected_by"] = calls_df["func"].map(infected_by)
    return calls_df


def find_io_infected_funcs(
    root: str,
    exclude: list[str] | None = None,
    io_funcs: tuple[str] = ("open", "input", "read", "write", "load", "save", "pd.read"),
) -> pd.DataFrame:
    exclude = exclude or []
    all_calls = []
    pkg_code = read_pkg_files(root, exclude)

    for name, data in pkg_code.items():
        tree = ast.parse(data)
        func_defs = get_funcs(tree)

        for func in func_defs:
            calls = get_calls(func)
            for call in calls:
                all_calls.append(
                    {
                        "module": name,
                        "func": func.name,
                        "line_no": call.func.lineno,
                        "calls": get_call_name(call.func),
                    }
                )

    calls_df = pd.DataFrame(all_calls)
    calls_df["module"] = calls_df["module"].apply(os.path.basename)
    calls_df["io_call"] = calls_df["calls"].str.startswith(tuple(io_funcs))
    calls_df["io_func"] = calls_df.groupby("func")["io_call"].transform("any")
    calls_df = propagate_io_infection(calls_df)
    calls_df["io_call"] = np.where(
        calls_df["calls"] == calls_df["infected_by"], True, calls_df["io_call"]
    )
    return calls_df[(calls_df["io_func"] & calls_df["io_call"])].convert_dtypes().fillna("")
