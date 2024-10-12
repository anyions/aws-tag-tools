from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("ElastiCache:Cluster")
class ElastiCacheClusterScanner(Scanner):
    def build_resource(self, client: any, cache: dict) -> AWSResource:
        arn = cache["ARN"]
        resource_tags = client.list_tags_for_resource(ResourceName=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            cache,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_cache_clusters").paginate()

        for page in paginator:
            for cache in page.get("CacheClusters", []):
                resources.append(self.build_resource(client, cache))

        return resources

    @property
    def _service_name(self) -> str:
        return "elasticache"

    @property
    def _arn_resource_type(self) -> str:
        return "cluster"

    @property
    def category(self) -> str:
        return "ElastiCache:Cluster"
