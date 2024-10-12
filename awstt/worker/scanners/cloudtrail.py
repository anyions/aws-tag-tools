from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudTrail")
class CloudTrailScanner(Scanner):
    def __init__(self, partition, _, credential):
        super().__init__(partition, ["global"], credential)

    def build_resource(self, client: any, trail: dict) -> AWSResource:
        arn = trail["TrailARN"]
        resource_tags = []
        for page in client.get_paginator("list_tags").paginate(ResourceIdList=[arn]):
            for item in page.get("ResourceTagList", []):
                resource_tags.extend(item.get("Items", []))

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags],
            trail,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_trails").paginate()

        for page in paginator:
            for trail in page.get("Trails", []):
                resources.append(self.build_resource(client, trail))

        return resources

    @property
    def _service_name(self) -> str:
        return "cloudtrail"

    @property
    def _arn_resource_type(self) -> str:
        return "trail"

    @property
    def category(self) -> str:
        return "CloudTrail"
