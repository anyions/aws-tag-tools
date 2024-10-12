from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:Instance")
class EC2Scanner(Scanner):
    def build_resource(self, client: any, instance: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, instance["InstanceId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in instance.get("Tags", [])],
            instance,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_instances").paginate()

        for page in paginator:
            for reservations in page.get("Reservations", []):
                for instance in reservations.get("Instances", []):
                    resources.append(self.build_resource(client, instance))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "instance"

    @property
    def category(self) -> str:
        return "EC2:Instance"
