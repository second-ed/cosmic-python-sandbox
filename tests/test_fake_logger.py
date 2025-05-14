from cosmic_python_sandbox.logger import FakeLogger


def test_fake_logger():
    logger = FakeLogger()
    logger.critical(0)
    logger.debug(1)
    logger.error(2)
    logger.fatal(3)
    logger.info(4)
    logger.notset(5)
    logger.warn(6)
    logger.warning(7)

    logger.log == [
        "CRITICAL: 0",
        "DEBUG: 1",
        "ERROR: 2",
        "FATAL: 3",
        "INFO: 4",
        "NOTSET: 5",
        "WARN: 6",
        "WARNING: 7",
    ]
