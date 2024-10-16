from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("Lambda:Function")
class LambdaFunctionScanner(Scanner):
    def build_resource(self, client: any, func: dict) -> AWSResource:
        resource_tags = client.list_tags(Resource=func["FunctionArn"])

        return AWSResource(
            self.category,
            self._build_arn(client, func["FunctionArn"]),
            [AWSResourceTag(key, value) for key, value in resource_tags.get("Tags", {}).items()],
            func,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_functions").paginate()

        for page in paginator:
            for func in page.get("Functions", []):
                resources.append(self.build_resource(client, func))

        return resources

    @property
    def _service_name(self) -> str:
        return "lambda"

    @property
    def _arn_resource_type(self) -> str:
        return "function"

    @property
    def category(self) -> str:
        return "Lambda:Function"
