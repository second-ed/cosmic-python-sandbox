def get_file_io_inf(path: str) -> str:
    with open(path) as f:
        return f.read()


def process_data_io_inf(path: str) -> str:
    data = get_file_io_inf(path)
    return upper_str_pure(data)


def upper_str_pure(inp_str: str) -> str:
    return inp_str.upper()
