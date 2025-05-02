from typing import Sequence

import black
import isort


def generate_fake_io(
    exts: Sequence[str],
    input_cmd: str = "read",
    output_cmd: str = "write",
    tab: str = "    ",
):
    init_lines = [
        "import os",
        "class FakeIO:",
        f"{tab}def __init__(self, db: dict = None, strict: bool = True):",
        f"{tab * 2}self.db = db or {{}}",
        f"{tab * 2}self.strict = strict",
    ]
    init = "\n".join(init_lines)

    check_file_lines = [
        f"{tab}def _check_file(self, path: str):",
        f"{tab * 2}if not self.strict:",
        f"{tab * 3}return\n",
        f"{tab * 2}if path not in self.db:",
        f'{tab * 3}raise FileNotFoundError(f"{{path}} not in db {{list(self.db.keys())}}")\n',
        f"{tab * 2}path_ext = os.path.splitext(path)[-1]",
        f"{tab * 2}if path_ext:",
        f"{tab * 3}if not path_ext.endswith(ext):",
        f'{tab * 4}raise ValueError(f"Path does not have expected ext: {{path = }} {{ext = }}")',
    ]
    check_file = "\n".join(check_file_lines)

    read_func_lines = [
        f"{tab}def _read(self, path: str, ext: str, **kwargs):",
        f"{tab * 2}self._check_file(path, ext)",
        f"{tab * 2}return self.db[path]",
    ]
    read_func = "\n".join(read_func_lines)

    write_func_lines = [
        f"{tab}def _write(self, data, path: str, **kwargs):",
        f"{tab * 2}self.db[path] = data",
        f"{tab * 2}return True",
    ]
    write_func = "\n".join(write_func_lines)

    reset_lines = [f"{tab}def reset(self):", f"{tab * 2}self.db = {{}}"]
    reset = "\n".join(reset_lines)

    funcs = [init, check_file, read_func, write_func, reset]

    for ext in exts:
        funcs.append(create_input_func(input_cmd, ext, tab))
        funcs.append(create_output_func(output_cmd, ext, tab))

    return format_code_str("\n\n".join(funcs))


def format_code_str(code_snippet: str) -> str:
    return black.format_str(isort.code(code_snippet), mode=black.FileMode())


def create_input_func(input_cmd: str, ext: str, tab: str):
    lines = [
        f"{tab}def {input_cmd}_{ext}(self, path: str, **kwargs):",
        f"{tab * 2}return self._read(path, '{ext}')",
    ]
    return "\n".join(lines)


def create_output_func(output_cmd: str, ext: str, tab: str):
    lines = [
        f"{tab}def {output_cmd}_{ext}(self, data, path: str, **kwargs):",
        f"{tab * 2}return self._write(data, path)",
    ]
    return "\n".join(lines)


def write_str(data: str, path: str):
    with open(path, "w") as f:
        f.write(data)
    return True
