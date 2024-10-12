from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudWatch:Rules")
class CloudWatchRulesScanner(Scanner):
    def build_resource(self, client: any, rule: dict) -> AWSResource:
        arn = rule["Arn"]
        resource_tags = client.list_tags_for_resource(ResourceARN=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            rule,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_rules").paginate()

        for page in paginator:
            for rule in page.get("Rules", []):
                resources.append(self.build_resource(client, rule))

        return resources

    @property
    def _service_name(self) -> str:
        return "events"

    @property
    def _arn_resource_type(self) -> str:
        return "rule"

    @property
    def category(self) -> str:
        return "CloudWatch:LogGroup"
