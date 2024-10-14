import logging
import os
import sys
from datetime import datetime
from typing import Any, Callable, Optional, Union


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


class FakePanel:
    pass


class FakeConsole:
    # noinspection PyMethodMayBeStatic
    def print(self, *objects, **kwargs):
        pass

    def print_json(
            self,
            json: Optional[str] = None,
            *,
            data: Any = None,
            indent: Union[None, int, str] = 2,
            highlight: bool = True,
            skip_keys: bool = False,
            ensure_ascii: bool = False,
            check_circular: bool = True,
            allow_nan: bool = True,
            default: Optional[Callable[[Any], Any]] = None,
            sort_keys: bool = False,
    ) -> None:
        pass

    def pprint(
            self,
            objects: Any,
    ) -> None:
        pass

    # noinspection PyMethodMayBeStatic
    def new_table(self, title: str, **_kwargs):
        return FakeTable(title)

    # noinspection PyMethodMayBeStatic
    def new_progress(self):
        return FakeProgress()

    # noinspection PyMethodMayBeStatic
    def new_panel(self, *_kwarg, **_kwargs):
        return FakePanel()

    # noinspection PyMethodMayBeStatic
    def new_pretty(self, *args, **kwargs):
        pass

    @staticmethod
    def is_fake():
        return True


if os.getenv("LAMBDA_TASK_ROOT") is None:
    from rich.console import Console as RichConsole
    from rich.panel import Panel as RichPanel
    from rich.pretty import Pretty, pprint
    from rich.progress import BarColumn
    from rich.progress import Progress as RichProgress
    from rich.progress import SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
    from rich.table import Table as RichTable


    class Console(RichConsole):
        # noinspection PyMethodMayBeStatic
        def new_table(self, title: str, **kwargs):
            return RichTable(title=title, **kwargs)

        # noinspection PyMethodMayBeStatic
        def new_progress(self):
            return RichProgress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self,
            )

        # noinspection PyMethodMayBeStatic
        def new_panel(self, *args, **kwargs):
            return RichPanel.fit(*args, **kwargs)

        # noinspection PyMethodMayBeStatic
        def new_pretty(self, *args, **kwargs):
            return Pretty(*args, **kwargs)

        def pprint(
                self,
                objects: Any,
        ) -> None:
            pprint(objects, console=self)

        @staticmethod
        def is_fake():
            return False

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


log_level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def init_logger(level: str = "error", save: bool = False):
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

    logging.getLogger().setLevel(log_level.get(level, logging.INFO))
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("boto").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger().addHandler(ShutdownHandler(level=logging.CRITICAL))
