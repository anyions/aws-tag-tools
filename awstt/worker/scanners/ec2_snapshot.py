from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:Snapshot")
class SnapshotScanner(Scanner):
    def _build_resource(self, client: any, snapshot: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, snapshot["SnapshotId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in snapshot.get("Tags", [])],
            snapshot,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_snapshots").paginate(**{"OwnerIds": ["self"]})

        for page in paginator:
            for snapshot in page.get("Snapshots", []):
                resources.append(self._build_resource(client, snapshot))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "snapshot"

    @property
    def category(self) -> str:
        return "EC2:Snapshot"