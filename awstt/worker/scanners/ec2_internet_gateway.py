from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:InternetGateway")
class InternetGatewayScanner(Scanner):
    def _build_resource(self, client: any, gateway: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, gateway["InternetGatewayId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in gateway.get("Tags", [])],
            gateway,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_internet_gateways").paginate()

        for page in paginator:
            for gateway in page.get("InternetGateways", []):
                resources.append(self._build_resource(client, gateway))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "internet-gateway"

    @property
    def category(self) -> str:
        return "EC2:InternetGateway"
