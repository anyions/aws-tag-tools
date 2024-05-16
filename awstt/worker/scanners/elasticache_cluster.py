# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("ElastiCache::Cluster")
class ElastiCacheClusterScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        clusters = item.get("CacheClusters", [])
        # noinspection DuplicatedCode
        for cluster in clusters:
            arn = cluster.get("ARN", None)
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
        return "describe_cache_clusters"

    @property
    def _arn_resource_type(self) -> str:
        return "cluster"

    @property
    def _tags_key(self) -> str:
        return "TagList"
