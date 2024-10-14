from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:VPNGateway")
class VPNGatewayScanner(Scanner):
    def _build_resource(self, client: any, gateway: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, gateway["VpnGatewayId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in gateway.get("Tags", [])],
            gateway,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = [client.describe_vpn_gateways()]

        for page in paginator:
            for gateway in page.get("VpnGateways", []):
                resources.append(self._build_resource(client, gateway))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "vpn-gateway"

    @property
    def category(self) -> str:
        return "EC2:VPNGateway"
