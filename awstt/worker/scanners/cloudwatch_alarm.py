# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("CloudWatch::Alarm")
class CloudWatchAlarmScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        alarms = []
        alarms.extend(item.get("CompositeAlarms", []))
        alarms.extend(item.get("MetricAlarms", []))

        for alarm in alarms:
            arn = alarm.get("AlarmArn", None)
            if arn is None:
                continue

            resource_tags = client.list_tags_for_resource(ResourceARN=arn)
            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "cloudwatch"

    @property
    def _paginator(self):
        return "describe_alarms"

    @property
    def _filters(self):
        return {}
