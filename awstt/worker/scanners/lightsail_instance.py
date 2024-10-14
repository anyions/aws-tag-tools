from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("Lightsail:Instance")
class LightsailScanner(Scanner):
    def build_resource(self, client: any, instance: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, instance["arn"]),
            [AWSResourceTag(tag["key"], tag["value"]) for tag in instance.get("tags", [])],
            instance,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("get_instances").paginate()

        for page in paginator:
            for instance in page.get("instances", []):
                resources.append(self.build_resource(client, instance))

        return resources

    @property
    def _service_name(self) -> str:
        return "lightsail"

    @property
    def _arn_resource_type(self) -> str:
        return "Instance"

    @property
    def category(self) -> str:
        return "Lightsail:Instance"
