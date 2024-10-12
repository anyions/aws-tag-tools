from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:EIP")
class EIPScanner(Scanner):
    def build_resource(self, client: any, address: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, address["AllocationId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in address.get("Tags", [])],
            address,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = [client.describe_addresses()]

        for page in paginator:
            for address in page.get("Addresses", []):
                resources.append(self.build_resource(client, address))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "eip"

    @property
    def category(self) -> str:
        return "EC2:EIP"
