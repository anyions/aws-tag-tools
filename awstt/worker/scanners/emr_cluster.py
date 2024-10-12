from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EMR:Cluster")
class EMRClusterScanner(Scanner):
    def build_resource(self, client: any, cluster: dict) -> AWSResource:
        detail = client.describe_cluster(ClusterId=cluster.get("Id")).get("Cluster", {})

        return AWSResource(
            self.category,
            self._build_arn(client, detail.get("ClusterArn")),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in detail.get("Tags", [])],
            detail,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_clusters").paginate()

        for page in paginator:
            for cluster in page.get("Clusters", []):
                resources.append(self.build_resource(client, cluster))

        return resources

    @property
    def _service_name(self) -> str:
        return "emr"

    @property
    def _arn_resource_type(self) -> str:
        return "cluster"

    @property
    def category(self) -> str:
        return "EMR:Cluster"
