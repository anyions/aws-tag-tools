from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:VPCPeering")
class VPCPeeringScanner(Scanner):
    def _build_resource(self, client: any, peering: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, peering["VpcPeeringConnectionId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in peering.get("Tags", [])],
            peering,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_vpc_peering_connections").paginate()

        for page in paginator:
            for peering in page.get("VpcPeeringConnections", []):
                resources.append(self._build_resource(client, peering))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "vpc-peering-connection"

    @property
    def category(self) -> str:
        return "EC2:VPCPeering"
