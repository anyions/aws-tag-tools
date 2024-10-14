from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:SecurityGroup")
class SecurityGroupScanner(Scanner):
    def _build_resource(self, client: any, group: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, group["GroupId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in group.get("Tags", [])],
            group,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_security_groups").paginate()

        for page in paginator:
            for group in page.get("SecurityGroups", []):
                resources.append(self._build_resource(client, group))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "security-group"

    @property
    def category(self) -> str:
        return "EC2:SecurityGroup"
