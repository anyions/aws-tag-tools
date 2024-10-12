from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("CloudWatch:Alarm")
class CloudWatchAlarmScanner(Scanner):
    def build_resource(self, client: any, alarm: dict) -> AWSResource:
        arn = alarm["AlarmArn"]
        resource_tags = client.list_tags_for_resource(ResourceARN=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            alarm,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_alarms").paginate()

        for page in paginator:
            alarms = []
            alarms.extend(page.get("CompositeAlarms", []))
            alarms.extend(page.get("MetricAlarms", []))

            for alarm in alarms:
                resources.append(self.build_resource(client, alarm))

        return resources

    @property
    def _service_name(self) -> str:
        return "cloudwatch"

    @property
    def _arn_resource_type(self) -> str:
        return "alarm"

    @property
    def category(self) -> str:
        return "CloudWatch:Alarm"
