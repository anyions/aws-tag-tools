from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("DynamoDB:Table")
class DynamoDBScanner(Scanner):
    def build_resource(self, client: any, table: dict) -> AWSResource:
        arn = self._build_arn(client, table.get("name"))
        resource_tags = client.list_tags_for_resource(ResourceArn=arn)

        return AWSResource(
            self.category,
            arn,
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            table,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_tables").paginate()

        for page in paginator:
            for table in page.get("TableNames", []):
                resources.append(self.build_resource(client, {"name": table}))

        return resources

    @property
    def _service_name(self) -> str:
        return "dynamodb"

    @property
    def _arn_resource_type(self) -> str:
        return "table"

    @property
    def category(self) -> str:
        return "DynamoDB:Table"
