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

namespace use_cases {
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