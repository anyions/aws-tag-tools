from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudFormation:Stack")
class CloudFormationScanner(Scanner):
    def build_resource(self, client: any, stack: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, stack["StackId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in stack.get("Tags", [])],
            stack,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_stacks").paginate()

        for page in paginator:
            for stack in page.get("Stacks", []):
                resources.append(self.build_resource(client, stack))

        return resources

    @property
    def _service_name(self) -> str:
        return "cloudformation"

    @property
    def _arn_resource_type(self) -> str:
        return "stack"

    @property
    def category(self) -> str:
        return "CloudFormation:Stack"
