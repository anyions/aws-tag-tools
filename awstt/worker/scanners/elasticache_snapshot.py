# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("ElastiCache::Snapshot")
class ElastiCacheSnapshotScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        snapshots = item.get("Snapshots", [])
        # noinspection DuplicatedCode
        for snapshot in snapshots:
            arn = snapshot.get("ARN", None)
            if arn is None:
                continue

            resource_tags = client.list_tags_for_resource(ResourceName=arn)
            if overwrite or not self._has_tag(resource_tags, key):
                resources.append((arn, self._get_tag(resource_tags, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "elasticache"

    @property
    def _paginator(self):
        return "describe_snapshots"

    @property
    def _arn_resource_type(self) -> str:
        return "snapshot"

    @property
    def _tags_key(self) -> str:
        return "TagList"
