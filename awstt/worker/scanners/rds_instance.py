# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("RDS::Instance")
class RDSInstanceScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        instances = item.get("DBInstances", [])
        for instance in instances:
            if overwrite is True or not self._has_tag(instance, key):
                resources.append((instance.get("DBInstanceArn"), self._get_tag(instance, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "rds"

    @property
    def _paginator(self):
        return "describe_db_instances"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "TagList"
