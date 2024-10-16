from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:Subnet")
class SubnetScanner(Scanner):
    def _build_resource(self, client: any, subnet: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, subnet["SubnetId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in subnet.get("Tags", [])],
            subnet,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_subnets").paginate()

        for page in paginator:
            for subnet in page.get("Subnets", []):
                resources.append(self._build_resource(client, subnet))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "subnet"

    @property
    def category(self) -> str:
        return "EC2:Subnet"
