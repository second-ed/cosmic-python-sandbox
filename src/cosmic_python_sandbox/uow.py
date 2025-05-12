import attrs

from cosmic_python_sandbox.fake_logger import LoggerProtocol


@attrs.define
class UnitOfWork:
    logger: LoggerProtocol = attrs.field()
    repo = attrs.field()
    guid: str = attrs.field()

    def __enter__(self):
        self.logger.info({"guid": self.guid, "msg": "Initialising UOW"})
        # any initialisation
        # self.repo.etc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error({"guid": self.guid, "msg": exc_val})
        else:
            self.logger.info({"guid": self.guid, "msg": "Completed UOW"})
        # close connection to repo
        # self.repo.etc()
