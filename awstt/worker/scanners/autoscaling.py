from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:AutoScalingGroup")
class AutoScalingGroupScanner(Scanner):
    def build_resource(self, client: any, group: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, group["AutoScalingGroupARN"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in group.get("Tags", [])],
            group,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_auto_scaling_groups").paginate()

        for page in paginator:
            for group in page.get("AutoScalingGroups", []):
                resources.append(self.build_resource(client, group))

        return resources

    @property
    def _service_name(self) -> str:
        return "autoscaling"

    @property
    def _arn_resource_type(self) -> str:
        return "autoscaling"

    @property
    def category(self) -> str:
        return "EC2:AutoScalingGroup"
