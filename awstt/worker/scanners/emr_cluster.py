# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EMR::Cluster")
class EMRClusterScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        clusters = item.get("Clusters", [])
        for cluster in clusters:
            arn = cluster.get("ClusterArn", None)
            cluster_id = cluster.get("Id", None)
            if arn is None or cluster_id is None:
                continue

            detail = client.describe_cluster(ClusterId=cluster_id).get("Cluster", {})
            if overwrite or not self._has_tag(detail, key):
                resources.append((arn, self._get_tag(detail, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "emr"

    @property
    def _paginator(self):
        return "list_clusters"

    @property
    def _filters(self):
        return {"ClusterStates": ["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"]}
