from typing import Literal, Sequence

import black
import isort


def generate_fake_io(
    db_exts: Sequence[str],
    external_exts: Sequence[str],
    hash_types: Sequence[str] = None,
    standard_ops: bool = True,
    input_cmd: str = "read",
    output_cmd: str = "write",
    tab: str = "    ",
) -> str:
    hash_types = hash_types or []

    init = (
        "from copy import deepcopy",
        "from typing import TypeVar",
        "import hashlib",
        "import os",
        "Data = TypeVar('Data')",
        "class FakeIO:",
        f"{tab}def __init__(self, db: dict = None, external_src: dict = None, strict: bool = True):",
        f"{tab * 2}self.db = db or {{}}",
        f"{tab * 2}self.external_src = external_src or {{}}",
        f"{tab * 2}self.log = []",
        f"{tab * 2}self.strict = strict",
    )

    funcs = [init]

    if db_exts:
        funcs.extend(get_db_funcs(tab))

    if standard_ops:
        funcs.extend(get_standard_ops(tab))

    for hash_type in hash_types:
        funcs.append(
            (
                f"{tab}def get_{hash_type}(self, path: str) -> str:",
                f"{tab * 2}self.log.append(('hash', path))",
                f"{tab * 2}return hashlib.md5(path.encode()).hexdigest()",
            )
        )

    for ext in db_exts:
        funcs.append(create_input_func(input_cmd, ext, tab))
        funcs.append(create_output_func(output_cmd, ext, tab))

    read_ext_src = (
        f"{tab}def _read_external_src(self, path: str, **kwargs) -> Data:",
        f"{tab * 2}self.log.append(('external_read', path, kwargs))",
        f"{tab * 2}return self.external_src[path]",
    )

    if external_exts:
        funcs.extend([read_ext_src])

    for src in external_exts:
        funcs.append(create_ext_input_func(src, tab))

    funcs = ("\n".join(lines) for lines in funcs)

    return format_code_str("\n\n".join(funcs))


def format_code_str(code_snippet: str) -> str:
    return black.format_str(isort.code(code_snippet), mode=black.FileMode())


def create_input_func(input_cmd: str, ext: str, tab: str) -> tuple[str]:
    lines = (
        f"{tab}def {input_cmd}_{ext}(self, path: str, **kwargs) -> Data:",
        f"{tab * 2}return self._read_db(path, '{ext}', **kwargs)",
    )
    return lines


def create_output_func(output_cmd: str, ext: str, tab: str) -> tuple[str]:
    lines = (
        f"{tab}def {output_cmd}_{ext}(self, data: Data, path: str, **kwargs) -> bool:",
        f"{tab * 2}return self._write_db(data, path, **kwargs)",
    )
    return lines


def create_ext_input_func(input_cmd: str, tab: str) -> tuple[str]:
    lines = (
        f"{tab}def {input_cmd}(self, path: str, **kwargs) -> Data:",
        f"{tab * 2}return self._read_external_src(path, **kwargs)",
    )
    return lines


def get_db_funcs(tab: str) -> tuple[str]:
    reset = (f"{tab}def reset_db(self):", f"{tab * 2}self.db = {{}}")

    check_file = (
        f"{tab}def _check_db(self, path: str) -> None:",
        f"{tab * 2}if path not in self.db:",
        f'{tab * 3}raise FileNotFoundError(f"{{path = }} not in {{list(self.db.keys()) = }}")\n',
        f"{tab * 2}if not self.strict:",
        f"{tab * 3}return\n",
        f"{tab * 2}path_ext = os.path.splitext(path)[-1]",
        f"{tab * 2}if path_ext != '':",
        f"{tab * 3}if not path_ext.endswith(ext):",
        f'{tab * 4}raise ValueError(f"Path does not have expected ext: {{path = }} {{ext = }}")',
    )

    read_func = (
        f"{tab}def _read_db(self, path: str, ext: str, **kwargs) -> Data:",
        f"{tab * 2}self.log.append(('read', path, kwargs))",
        f"{tab * 2}self._check_db(path)",
        f"{tab * 2}return self.db[path]",
    )

    write_func = (
        f"{tab}def _write_db(self, data: Data, path: str, **kwargs) -> bool:",
        f"{tab * 2}self.log.append(('write', path, kwargs))",
        f"{tab * 2}self.db[path] = data",
        f"{tab * 2}return True",
    )

    return reset, check_file, read_func, write_func


def get_standard_ops(tab):
    copy_func = (
        f"{tab}def copy(self, path: str, new_path: str) -> bool:",
        f"{tab * 2}self.log.append(('copy', path, new_path))",
        f"{tab * 2}data = deepcopy(self.db[path])",
        f"{tab * 2}self.db[new_path] = data",
        f"{tab * 2}return True",
    )
    move_func = (
        f"{tab}def move(self, path: str, new_path: str) -> bool:",
        f"{tab * 2}self.log.append(('move', path, new_path))",
        f"{tab * 2}data = deepcopy(self.db[path])",
        f"{tab * 2}self.db[new_path] = data",
        f"{tab * 2}self.db.pop(path)",
        f"{tab * 2}return True",
    )
    remove_func = (
        f"{tab}def remove(self, path: str) -> bool:",
        f"{tab * 2}self.log.append(('remove', path))",
        f"{tab * 2}self.db.pop(path)",
        f"{tab * 2}return True",
    )
    exists_func = (
        f"{tab}def is_file(self, path: str) -> bool:",
        f"{tab * 2}self.log.append(('is_file', path))",
        f"{tab * 2}return path in self.db",
    )
    list_files_func = (
        f"{tab}def list_files(self, prefix: str = '') -> list[str]:",
        f"{tab * 2}self.log.append(('list_files', path))",
        f"{tab * 2}return [p for p in self.db if p.startswith(prefix)]",
    )
    size_func = (
        f"{tab}def get_size(self, path: str) -> int:",
        f"{tab * 2}self.log.append(('size', path))",
        f"{tab * 2}return len(path.encode('utf-8'))",
    )
    return copy_func, move_func, remove_func, exists_func, list_files_func, size_func


def write_str(data: str, path: str) -> Literal[True]:
    with open(path, "w") as f:
        f.write(data)
    return True
