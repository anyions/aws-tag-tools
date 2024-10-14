from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("RDS:Cluster")
class RDSClusterScanner(Scanner):
    def build_resource(self, client: any, cluster: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, cluster["DBClusterArn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in cluster.get("TagList", [])],
            cluster,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_db_clusters").paginate()

        for page in paginator:
            for cluster in page.get("DBClusters", []):
                resources.append(self.build_resource(client, cluster))

        return resources

    @property
    def _service_name(self) -> str:
        return "rds"

    @property
    def _arn_resource_type(self) -> str:
        return "cluster"

    @property
    def category(self) -> str:
        return "RDS:Cluster"
