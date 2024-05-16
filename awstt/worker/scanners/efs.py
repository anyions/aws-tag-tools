# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EFS")
class EFSScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        systems = item.get("FileSystems", [])
        for system in systems:
            if overwrite is True or not self._has_tag(system, key):
                arn = system.get("FileSystemArn")
                resources.append((arn, self._get_tag(system, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "efs"

    @property
    def _paginator(self):
        return "describe_file_systems"

    @property
    def _filters(self):
        return {}
