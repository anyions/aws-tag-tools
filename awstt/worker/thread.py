import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from awstt import output
from awstt.worker.scanner import Scanner
from awstt.worker.tagger import Tagger
from awstt.worker.types import (
    AWSResource,
    RegionalTaggingTarget,
    ResourceFilter,
    TaggingResponse,
)


logger = logging.getLogger(__name__)

SCANNING_THREAD_LIMIT = 10
RATE_LIMIT_EXCEEDED = "Rate exceeded"


class ScanningThread:
    _workers: List["ScanningThread.Worker"] = []

    class Worker:
        def __init__(self, scanner: Scanner, filters: List[ResourceFilter]):
            self.scanner = scanner
            self.filters = filters

        def execute(self) -> List[AWSResource]:
            resources = []
            try:
                resources = self.scanner.execute(filters=self.filters)
            except KeyboardInterrupt:
                logger.warning(f"Scanning process terminated - {self.scanner.category}")
            except Exception as e:
                logger.error(f"Scanning process failed - {self.scanner.category}, error - {e}")
            finally:
                return resources

    @classmethod
    def add(cls, scanner: Scanner, filters: list[ResourceFilter]):
        cls._workers.append(ScanningThread.Worker(scanner, filters))

    @classmethod
    def execute(cls, console: output.Console) -> List[AWSResource]:
        logger.debug(f"Executing resources scan, total - {len(cls._workers)}")

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
        logger.debug(f"Finished resources scan, found - {len(resources)}")

        return resources


class TaggingThread:
    _workers: List["TaggingThread.Worker"] = []

    class Worker:
        def __init__(self, targets: List[RegionalTaggingTarget]):
            self.targets = targets

        def execute(self, tagger: Tagger) -> List[TaggingResponse]:
            t_dict = [target.dict() for target in self.targets]

            responses = []
            try:
                responses = tagger.execute(self.targets)
            except KeyboardInterrupt:
                logger.warning(f"Tags set/unset process terminated, targets - {t_dict}")
            except Exception as e:
                logger.error(f"Tags set/unset process failed, targets - {t_dict}, exception - {e}")
            finally:
                return responses

        @property
        def total_targets(self) -> int:
            total = 0
            for target in self.targets:
                total += len(target.resources)

            return total

    @classmethod
    def add(cls, targets: List[RegionalTaggingTarget]):
        cls._workers.append(TaggingThread.Worker(targets))

    @classmethod
    def execute(cls, tagger: Tagger, console: output.Console) -> List[TaggingResponse]:
        logger.debug(f"Executing resources tagging...")

        progress = console.new_progress()
        progress.add_task("Tagging...".ljust(15), total=None)
        progress.start()

        rate_exceeded_targets = []

        responses = []
        for worker in cls._workers:
            resp = worker.execute(tagger=tagger)
            for r in resp:
                if r.hint != RATE_LIMIT_EXCEEDED:
                    responses.append(r)
                else:
                    for target in worker.targets:
                        for res in target.resources:
                            if res.arn == r.arn:
                                rate_exceeded_targets.append((target.region, res, target.tags))

        while 1:
            if len(rate_exceeded_targets) == 0:
                break

            targets_map = {}
            for item in rate_exceeded_targets:
                region, res, tags = item[0], item[1], item[2]
                tag_str = ",".join([f"{t.key}={t.value}" for t in tags])

                if region not in targets_map:
                    targets_map[region] = {}
                region_map = targets_map[region]
                if tag_str not in region_map:
                    region_map[tag_str] = {"tags": tags, "resources": []}
                region_map[tag_str]["resources"].append(res)

            regional_targets: List[RegionalTaggingTarget] = []
            for region, targets in targets_map.items():
                for _, tag_group in targets.items():
                    regional_targets.append(RegionalTaggingTarget(region, tag_group["resources"], tag_group["tags"]))

            resp = tagger.execute(regional_targets)
            for r in resp:
                if r.hint != RATE_LIMIT_EXCEEDED:
                    responses.append(r)
                    for item in rate_exceeded_targets:
                        if item[1].arn == r.arn:
                            rate_exceeded_targets.remove(item)

            if len(rate_exceeded_targets) > 0:
                time.sleep(0.3)  # avoid throttling

        progress.stop()
        logger.debug(f"Finished batch resources tagging")

        responses.sort(key=lambda x: f"{x.category}--{x.arn}")
        return responses
