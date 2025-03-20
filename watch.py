from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable

class Handler(FileSystemEventHandler):
    def __init__(self, settle: float, callback: Callable[[str], None]):
        self.callback = callback
        self.settle = settle
        self.last_modified = None
        self.timer: Timer | None = None

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        if self.timer is not None:
            self.timer.cancel()
        self.timer = Timer(self.settle, self._debounced_callback, [event.event_type])
        self.timer.start()

    def _debounced_callback(self, event_type: str) -> None:
        self.timer = None
        self.callback(event_type)

def watch(paths: list[str], settle: float, callback: Callable[[str], None]):
    handler = Handler(settle, callback)
    observer = Observer()
    for path in paths:
        print(f'watching {path}')
        observer.schedule(handler, path=path, recursive=True)
    observer.start()

    # daemon implementation
    while observer.is_alive():
        observer.join(1)

    # stub for non-daemon
    # try: 
    #     while observer.is_alive():
    #         observer.join(1)
    # finally: 
    #     observer.stop()
    # observer.join()
