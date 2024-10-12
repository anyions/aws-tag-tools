from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudWatch:LogGroup")
class CloudWatchLogGroupScanner(Scanner):
    def build_resource(self, client: any, group: dict) -> AWSResource:
        arn = group["arn"][:-2] if group["arn"].endswith(":*") else group["arn"]  # remove ':*' from response
        resource_tags = client.list_tags_for_resource(resourceArn=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(key, value) for key, value in resource_tags.get("tags", {}).items()],
            group,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_log_groups").paginate()

        for page in paginator:
            for group in page.get("logGroups", []):
                resources.append(self.build_resource(client, group))

        return resources

    @property
    def _service_name(self) -> str:
        return "logs"

    @property
    def _arn_resource_type(self) -> str:
        return "log-group"

    @property
    def category(self) -> str:
        return "CloudWatch:LogGroup"
