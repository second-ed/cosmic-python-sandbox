from cosmic_python_sandbox.adapters.io_mod import FakeIO
from cosmic_python_sandbox.adapters.logger import FakeLogger
from cosmic_python_sandbox.service_layer.message_bus import MessageBus
from cosmic_python_sandbox.service_layer.uow import UnitOfWork
from cosmic_python_sandbox.usecases.events import CopyFile
from cosmic_python_sandbox.usecases.handlers import EVENT_HANDLERS

if __name__ == "__main__":
    # add bootstrapping stuff here
    # essentially config
    logger = FakeLogger()
    uow = UnitOfWork(repo=FakeIO(), logger=logger)

    # where the stuff happens
    starting_events = [CopyFile(src="some/path.csv", dst="to/path.csv")]
    bus = MessageBus(uow=uow, event_handlers=EVENT_HANDLERS)
    bus.add_events(starting_events)
    bus.handle_events()
