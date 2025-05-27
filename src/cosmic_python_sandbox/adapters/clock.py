import datetime as dt


def clock_now(date_fmt: str = "%y%m%d_%H%M%S") -> str:
    return dt.datetime.now(dt.timezone.utc).strftime(date_fmt)


def fake_clock_now(_: str = "%y%m%d_%H%M%S") -> str:
    return "20250527_194000"
