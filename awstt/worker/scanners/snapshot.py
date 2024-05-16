# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2:Snapshot")
class SnapshotScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        snapshots = item.get("Snapshots", [])
        for snapshot in snapshots:
            if overwrite is True or not self._has_tag(snapshot, key):
                arn = self._build_arn(client, snapshot.get("SnapshotId"))
                resources.append((arn, self._get_tag(snapshot, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _paginator(self):
        return "describe_snapshots"

    @property
    def _arn_resource_type(self) -> str:
        return "snapshot"

    @property
    def _filters(self):
        return {"OwnerIds": ["self"]}
