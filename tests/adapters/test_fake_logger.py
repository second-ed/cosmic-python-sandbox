from cosmic_python_sandbox.adapters.logger import FakeLogger


def test_fake_logger():
    logger = FakeLogger()
    logger.debug(0)
    logger.error(1)
    logger.info(2)

    assert logger.log == [
        "DEBUG: 0",
        "ERROR: 1",
        "INFO: 2",
    ]
