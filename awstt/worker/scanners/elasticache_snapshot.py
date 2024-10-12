from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("ElastiCache:Snapshot")
class ElastiCacheSnapshotScanner(Scanner):
    def build_resource(self, client: any, snapshot: dict) -> AWSResource:
        arn = snapshot["ARN"]
        resource_tags = client.list_tags_for_resource(ResourceName=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("TagList", [])],
            snapshot,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_snapshots").paginate()

        for page in paginator:
            for snapshot in page.get("Snapshots", []):
                resources.append(self.build_resource(client, snapshot))

        return resources

    @property
    def _service_name(self) -> str:
        return "elasticache"

    @property
    def _arn_resource_type(self) -> str:
        return "snapshot"

    @property
    def category(self) -> str:
        return "ElastiCache:Snapshot"
