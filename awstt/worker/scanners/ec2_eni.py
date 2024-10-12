from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:ENI")
class ENIScanner(Scanner):
    def build_resource(self, client: any, eni: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, eni["NetworkInterfaceId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in eni.get("TagSet", [])],
            eni,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_network_interfaces").paginate()

        for page in paginator:
            for eni in page.get("NetworkInterfaces", []):
                resources.append(self.build_resource(client, eni))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "network-interface"

    @property
    def category(self) -> str:
        return "EC2:EIP"
