from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:NetworkACL")
class NetworkACLScanner(Scanner):
    def _build_resource(self, client: any, gateway: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, gateway["NetworkAclId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in gateway.get("Tags", [])],
            gateway,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_network_acls").paginate()

        for page in paginator:
            for gateway in page.get("NetworkAcls", []):
                resources.append(self._build_resource(client, gateway))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "network-acl"

    @property
    def category(self) -> str:
        return "EC2:NetworkACL"
