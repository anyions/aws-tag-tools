from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudFront:Distribution")
class CloudFrontScanner(Scanner):
    def __init__(self, partition, _, credential):
        if partition in ["aws", "aws-gov"]:
            super().__init__(partition, ["global"], credential)
        else:
            super().__init__(partition, ["cn-northwest-1", "cn-northeast-1"], credential)

    def build_resource(self, client: any, dist: dict) -> AWSResource:
        arn = dist["ARN"]
        resource_tags = client.list_tags_for_resource(Resource=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", {}).get("Items", [])],
            dist,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_distributions").paginate()

        for page in paginator:
            distributions = page.get("DistributionList", {})
            for dist in distributions.get("Items", []):
                resources.append(self.build_resource(client, dist))

        return resources

    @property
    def _service_name(self) -> str:
        return "cloudfront"

    @property
    def _arn_resource_type(self) -> str:
        return "distribution"

    @property
    def category(self) -> str:
        return "CloudFront"
