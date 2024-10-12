import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from awstt import output
from awstt.worker.scanner import Scanner
from awstt.worker.tagger import Tagger
from awstt.worker.types import AWSResource, RegionalTaggingTarget, ResourceSelector, TaggingResponse


logger = logging.getLogger(__name__)

SCANNING_THREAD_LIMIT = 5
TAGGING_THREAD_LIMIT = 1


class ScanningThread:
    _workers = []

    class Worker:
        def __init__(self, scanner: Scanner, selectors: List[ResourceSelector]):
            self.scanner = scanner
            self.selectors = selectors

        def execute(self) -> List[AWSResource]:
            resources = []
            try:
                resources = self.scanner.execute(selectors=self.selectors)
            except KeyboardInterrupt:
                logger.warning(f"Scanning process terminated - {self.scanner.category}")
            except Exception as e:
                logger.error(f"Scanning process failed - {self.scanner.category}, error - {e}")
            finally:
                return resources

    @classmethod
    def add(cls, scanner: Scanner, selectors: list[ResourceSelector]):
        cls._workers.append(ScanningThread.Worker(scanner, selectors))

    @classmethod
    def execute(cls, console: output.Console) -> List[AWSResource]:
        logger.info(f"Executing resources scan, total - {len(cls._workers)}")

        resources = []
        with ThreadPoolExecutor(max_workers=SCANNING_THREAD_LIMIT) as executor:
            progress = console.new_progress()
            task_id = progress.add_task("Scanning...".ljust(15), total=len(cls._workers))
            progress.start()

            futures = [executor.submit(worker.execute) for worker in cls._workers]
            for future in as_completed(futures):
                progress.update(task_id, advance=1)
                resources.extend(future.result())

        progress.stop()
        logger.info(f"Finished resources scan, found - {len(resources)}")

        return resources


class TaggingThread:
    _workers = []

    class Worker:
        def __init__(self, tagger: Tagger, targets: List[RegionalTaggingTarget]):
            self.tagger = tagger
            self.targets = targets

        def execute(self) -> List[TaggingResponse]:
            t_dict = [target.dict() for target in self.targets]

            responses = []
            try:
                responses = self.tagger.execute(self.targets)
            except KeyboardInterrupt:
                logger.warning(f"Resources tagging process terminated, targets - {t_dict}")
            except Exception as e:
                logger.error(f"Resources tagging process failed, targets - {t_dict}, exception - {e}")
            finally:
                return responses

        @property
        def total_targets(self) -> int:
            total = 0
            for target in self.targets:
                total += len(target.resources)

            return total

    @classmethod
    def add(cls, tagger: Tagger, targets: List[RegionalTaggingTarget]):
        cls._workers.append(TaggingThread.Worker(tagger, targets))

    @classmethod
    def execute(cls, console: output.Console) -> List[TaggingResponse]:
        logger.info(f"Executing resources tagging...")

        progress = console.new_progress()
        task_id = progress.add_task("Tagging...".ljust(15), total=sum(worker.total_targets for worker in cls._workers))
        progress.start()

        responses = []
        with ThreadPoolExecutor(max_workers=TAGGING_THREAD_LIMIT) as executor:
            futures = [executor.submit(worker.execute) for worker in cls._workers]
            for future in as_completed(futures):
                resp = future.result()
                progress.update(task_id, advance=len(resp))
                responses.extend(resp)

        progress.stop()
        logger.info(f"Finished batch resources tagging")

        responses.sort(key=lambda x: f"{x.category}--{x.arn}")
        return responses
