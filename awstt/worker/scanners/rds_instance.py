from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("RDS:Instance")
class RDSInstanceScanner(Scanner):
    def build_resource(self, client: any, cluster: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, cluster["DBClusterArn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in cluster.get("TagList", [])],
            cluster,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_db_instances").paginate()

        for page in paginator:
            for instance in page.get("DBInstances", []):
                resources.append(self.build_resource(client, instance))

        return resources

    @property
    def _service_name(self) -> str:
        return "rds"

    @property
    def _arn_resource_type(self) -> str:
        return "db"

    @property
    def category(self) -> str:
        return "RDS:Instance"
