# Place to mess about with the ideas from the cosmic python book

```mermaid
classDiagram

namespace adapters {
    class FileSystemProtocol {
        +list(root: str)
        +copy(from: str, to: str)
        +move(from: str, to: str)
        +delete(path: str)
    }

    class FakeFS
    class LocalFS
    class HDFS


    class IOProtocol {
        +setup()
        +teardown()
        +read(path: str, file_type: FileType)
        +write(path: str, data: Data)
    }

    class FakeIO
    class PandasIO
    class PolarsIO


    class LoggerProtocol {
        +info()
        +debug()
        +error()
    }

    class FakeLogger {
        log: list
    }
    class RealLogger

    class RepoProtocol {
        fs: FileSystemProtocol
        io: IOProtocol
    }
}

namespace usecases {
    class Event {
        priority_event: bool
    }

    class parse_events
    class event_handlers
}

namespace service_layer{
    class UnitOfWork {
        logger: LoggerProtocol
        repo: RepoProtocol
        clock_func: Callable[[str], str]
        guid_func: Callable[[], str]
        +__enter__()
        +__exit__()
    }

    class MessageBus {
        event_handlers: dict[Event, Callable]
        uow: UnitOfWork
        queue: Queue or deque
        +add_events()
        +handle_event()
        +handle_events()
    }
}

LoggerProtocol <|.. FakeLogger
LoggerProtocol <|.. RealLogger

IOProtocol <|.. FakeIO
IOProtocol <|.. PandasIO
IOProtocol <|.. PolarsIO

RepoProtocol *-- FileSystemProtocol
RepoProtocol *-- IOProtocol

parse_events --> Event : decodes from json
Event --> event_handlers : handles

FileSystemProtocol <|.. FakeFS
FileSystemProtocol <|.. LocalFS
FileSystemProtocol <|.. HDFS

UnitOfWork *-- LoggerProtocol
UnitOfWork *-- RepoProtocol

MessageBus --> UnitOfWork
MessageBus *-- event_handlers

```

# Repo map
```
├── .github
│   └── workflows
│       └── ci_tests.yaml
├── src
│   └── cosmic_python_sandbox
│       ├── adapters
│       │   ├── fs_wrappers
│       │   │   ├── __init__.py
│       │   │   ├── _fs_protocol.py
│       │   │   └── local_fs_wrapper.py
│       │   ├── io_wrappers
│       │   │   ├── __init__.py
│       │   │   ├── _io_protocol.py
│       │   │   ├── pd_io.py
│       │   │   └── pl_io.py
│       │   ├── __init__.py
│       │   ├── clock.py
│       │   ├── logger.py
│       │   └── repo.py
│       ├── domain
│       │   └── __init__.py
│       ├── service_layer
│       │   ├── __init__.py
│       │   ├── message_bus.py
│       │   └── uow.py
│       ├── usecases
│       │   ├── __init__.py
│       │   ├── _event.py
│       │   ├── copy_file.py
│       │   ├── delete_file.py
│       │   └── move_file.py
│       ├── utils
│       │   ├── __init__.py
│       │   ├── detect_io_infection.py
│       │   └── fake_io_generation.py
│       ├── __init__.py
│       └── __main__.py
├── tests
│   ├── adapters
│   │   ├── __init__.py
│   │   └── test_fake_logger.py
│   ├── service_layer
│   │   ├── __init__.py
│   │   └── test_message_bus.py
│   ├── usecases
│   │   ├── __init__.py
│   │   ├── test_events.py
│   │   └── test_handlers.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── test_detect_io_infection.py
│   │   └── test_fake_io_generation.py
│   ├── __init__.py
│   └── test_fakes_api.py
├── README.md
├── pyproject.toml
├── ruff.toml
└── uv.lock
::
```