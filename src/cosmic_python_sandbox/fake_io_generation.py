from typing import Sequence

import black
import isort


def generate_fake_io(
    db_exts: Sequence[str],
    external_exts: Sequence[str],
    input_cmd: str = "read",
    output_cmd: str = "write",
    tab: str = "    ",
):
    init = "\n".join(
        [
            "import os",
            "class FakeIO:",
            f"{tab}def __init__(self, db: dict = None, external_src: dict = None, strict: bool = True):",
            f"{tab * 2}self.db = db or {{}}",
            f"{tab * 2}self.external_src = external_src or {{}}",
            f"{tab * 2}self.strict = strict",
        ]
    )

    check_file = "\n".join(
        [
            f"{tab}def _check_db(self, path: str):",
            f"{tab * 2}if not self.strict:",
            f"{tab * 3}return\n",
            f"{tab * 2}if path not in self.db:",
            f'{tab * 3}raise FileNotFoundError(f"{{path}} not in db {{list(self.db.keys())}}")\n',
            f"{tab * 2}path_ext = os.path.splitext(path)[-1]",
            f"{tab * 2}if path_ext:",
            f"{tab * 3}if not path_ext.endswith(ext):",
            f'{tab * 4}raise ValueError(f"Path does not have expected ext: {{path = }} {{ext = }}")',
        ]
    )

    read_func = "\n".join(
        [
            f"{tab}def _read_db(self, path: str, ext: str, **kwargs):",
            f"{tab * 2}self._check_db(path, ext)",
            f"{tab * 2}return self.db[path]",
        ]
    )

    write_func = "\n".join(
        [
            f"{tab}def _write_db(self, data, path: str, **kwargs):",
            f"{tab * 2}self.db[path] = data",
            f"{tab * 2}return True",
        ]
    )

    reset = "\n".join([f"{tab}def reset(self):", f"{tab * 2}self.db = {{}}"])

    funcs = [init, reset]

    if db_exts:
        funcs.extend([check_file, read_func, write_func])

    for ext in db_exts:
        funcs.append(create_input_func(input_cmd, ext, tab))
        funcs.append(create_output_func(output_cmd, ext, tab))

    read_ext_src = "\n".join(
        [
            f"{tab}def _read_external_src(self, path: str, **kwargs):",
            f"{tab * 2}return self.external_src[path]",
        ]
    )

    if external_exts:
        funcs.extend([read_ext_src])

    for src in external_exts:
        funcs.append(create_ext_input_func(src, tab))

    return format_code_str("\n\n".join(funcs))


def format_code_str(code_snippet: str) -> str:
    return black.format_str(isort.code(code_snippet), mode=black.FileMode())


def create_input_func(input_cmd: str, ext: str, tab: str):
    lines = [
        f"{tab}def {input_cmd}_{ext}(self, path: str, **kwargs):",
        f"{tab * 2}return self._read_db(path, '{ext}')",
    ]
    return "\n".join(lines)


def create_output_func(output_cmd: str, ext: str, tab: str):
    lines = [
        f"{tab}def {output_cmd}_{ext}(self, data, path: str, **kwargs):",
        f"{tab * 2}return self._write_db(data, path)",
    ]
    return "\n".join(lines)


def create_ext_input_func(input_cmd: str, tab: str):
    lines = [
        f"{tab}def {input_cmd}(self, path: str, **kwargs):",
        f"{tab * 2}return self._read_external_src(path)",
    ]
    return "\n".join(lines)


def write_str(data: str, path: str):
    with open(path, "w") as f:
        f.write(data)
    return True
