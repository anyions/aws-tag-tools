# -*- coding: utf-8 -*-

import logging
import time
from multiprocessing import Pipe, Process, Semaphore
from typing import List, Optional

from awstt.worker import *


logger = logging.getLogger(__name__)

PROCESS_SCAN_CONCURRENCY = 5


def _scan_in_process(
    sema: Semaphore,
    pipe: Pipe,
    worker_name: str,
    tag_key: str,
    account_id: str,
    partition: str,
    regions: List[str],
    profile: Optional[str] = None,
    overwrite: Optional[bool] = False,
):
    output = []

    try:
        sema.acquire()

        logger.info(f"resource scan is starting - {worker_name}")
        process_scanner = Scanner.by_name(worker_name)(
            account_id,
            partition=partition,
            regions=regions,
            profile=profile,
        )
        logger.info(f"resource scan is working - {worker_name}@{process_scanner.available_regions}")

        output = process_scanner.execute(key=tag_key, overwrite=overwrite)

        logger.info(f"resource scan is finished - {worker_name}")
    except KeyboardInterrupt:
        logger.warning(f"resource scan is terminated - {worker_name}")
    except Exception as e:
        logger.error(f"resource scan is failed - {worker_name}, exception - {e}")
    finally:
        pipe.send(output)
        pipe.close()
        sema.release()


def execute(evt: any, _):
    start = time.time()

    sema = Semaphore(PROCESS_SCAN_CONCURRENCY)
    processes = []
    output_pipes = []

    try:
        account_id = detect_account_id(evt.get("profile", None))
        partition = detect_partition(evt.get("partition", None))
        regions = detect_regions(evt.get("regions", None))
        profile = evt.get("profile", None)
        tag_key = evt.get("tag_key")
        tag_value = evt.get("tag_value")
        overwrite = evt.get("overwrite", False)

        params = dict(
            account_id=account_id,
            partition=partition,
            regions=regions,
            profile=profile,
            tag_key=tag_key,
            tag_value=tag_value,
            overwrite=overwrite,
        )

        logger.info(f"executing with params: {params}")

        for name in Scanner.list_available():
            parent_conn, child_conn = Pipe()
            output_pipes.append(parent_conn)

            kwargs = {"sema": sema, "worker_name": name, "pipe": child_conn, **params}
            kwargs.pop("tag_value")

            p = Process(target=_scan_in_process, kwargs=kwargs)
            processes.append(p)
            p.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        regional_resources = {}
        for pipe in output_pipes:
            outputs = pipe.recv()

            for item in outputs:
                regional_resources[item[0]] = regional_resources.get(item[0], []) + item[1]

        logger.info(f"tagger now is running...")
        final_tagger = Tagger(account_id, partition=partition, profile=profile)
        final_tagger.execute(key=tag_key, value=tag_value, regional_resources=regional_resources)
        logger.info(f"tagger execute finished")

        logger.info(f"execute finished, total time used - {round(time.time() - start, 2)}s")
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
    except Exception as e:
        logger.error(f"Failed to execute, exception - {e}")
