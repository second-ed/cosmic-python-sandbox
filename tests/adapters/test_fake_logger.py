from cosmic_python_sandbox.adapters.logger import FakeLogger


def test_fake_logger():
    logger = FakeLogger()
    logger.critical(0)
    logger.debug(1)
    logger.error(2)
    logger.fatal(3)
    logger.info(4)
    logger.notset(5)
    logger.warning(6)

    assert logger.log == [
        "CRITICAL: 0",
        "DEBUG: 1",
        "ERROR: 2",
        "FATAL: 3",
        "INFO: 4",
        "NOTSET: 5",
        "WARNING: 6",
    ]
