from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:EBS")
class EBSScanner(Scanner):
    def build_resource(self, client: any, volume: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, volume["VolumeId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in volume.get("Tags", [])],
            volume,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_volumes").paginate()

        for page in paginator:
            for volume in page.get("Volumes", []):
                resources.append(self.build_resource(client, volume))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "volume"

    @property
    def category(self) -> str:
        return "EC2:EBS"
