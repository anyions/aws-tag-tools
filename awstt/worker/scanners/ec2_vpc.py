from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:VPC")
class VPCScanner(Scanner):
    def _build_resource(self, client: any, vpc: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, vpc["VpcId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in vpc.get("Tags", [])],
            vpc,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_vpcs").paginate()

        for page in paginator:
            for vpc in page.get("Vpcs", []):
                resources.append(self._build_resource(client, vpc))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "vpc"

    @property
    def category(self) -> str:
        return "EC2:VPC"
