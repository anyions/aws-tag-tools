# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("RDS::Cluster")
class RDSClusterScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        clusters = item.get("DBClusters", [])
        for cluster in clusters:
            if overwrite is True or not self._has_tag(cluster, key):
                resources.append((cluster.get("DBClusterArn"), self._get_tag(cluster, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "rds"

    @property
    def _paginator(self):
        return "describe_db_clusters"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "TagList"
