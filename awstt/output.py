import logging
import os
import sys
from datetime import datetime
from typing import Optional


class FakeColumn:
    def __init__(self, _name: str, _width: Optional[int] = None):
        pass


class FakeRow:
    def __init__(self, *values, _end_section: bool = False):
        pass


class FakeTable:
    def __init__(self, _title: str):
        pass

    def add_section(self):
        pass

    def add_column(self, name: str, width: Optional[int] = None):
        pass

    def add_row(self, *values, end_section: bool = False):
        pass


class FakeProgress:
    def __init__(self):
        self.tasks = []

    def add_task(self, description: str, total: float = 100.0):
        self.tasks.append((description, total))
        return len(self.tasks) + 1

    def update(self, task_id: int, advance: float = 1.0):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def remove_task(self, task_id: int):
        pass


class FakeConsole:
    # noinspection PyMethodMayBeStatic
    def print(self, table: FakeTable):
        pass

    # noinspection PyMethodMayBeStatic
    def new_table(self, title: str):
        return FakeTable(title)

    # noinspection PyMethodMayBeStatic
    def new_progress(self):
        return FakeProgress()


if os.getenv("LAMBDA_TASK_ROOT") is None:
    from rich.console import Console as RichConsole
    from rich.progress import Progress as RichProgress
    from rich.table import Table as RichTable

    class Console(RichConsole):
        # noinspection PyMethodMayBeStatic
        def new_table(self, title: str):
            return RichTable(title=title)

        # noinspection PyMethodMayBeStatic
        def new_progress(self):
            return RichProgress(console=self)

else:
    Console = FakeConsole

__console = None


def console() -> Console:
    global __console
    if __console is None:
        __console = Console()
    return __console


class ShutdownHandler(logging.Handler):
    def emit(self, record):
        logging.shutdown()
        sys.exit(1)


def init_logger(debug: bool = False, save: bool = False):
    if os.getenv("LAMBDA_TASK_ROOT") is None:
        from rich.highlighter import NullHighlighter
        from rich.logging import RichHandler

        logging.basicConfig(
            handlers=[
                RichHandler(
                    console=console(),
                    omit_repeated_times=False,
                    # log_time_format="[%Y-%m-%d %H:%M:%S]",
                    highlighter=NullHighlighter(),
                ),
            ],
            format="%(message)s",
        )

        if save:
            file_handler = logging.FileHandler(f"awstt-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
            file_handler.setFormatter(
                logging.Formatter("[%(asctime)s] | %(levelname)-8s | %(name)s:%(lineno)s - %(message)s")
            )
            logging.getLogger().addHandler(file_handler)
    else:
        import boto3

        boto3.set_stream_logger("", logging.INFO)

    logging.getLogger().setLevel(logging.DEBUG if debug else logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("boto").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger().addHandler(ShutdownHandler(level=50))
