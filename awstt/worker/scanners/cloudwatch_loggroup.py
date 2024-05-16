# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("CloudWatch::LogGroup")
class CloudWatchAlarmScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        groups = item.get("logGroups", [])

        for group in groups:
            arn = group.get("arn", None)
            if arn is None:
                continue

            resource_tags = client.list_tags_for_resource(resourceArn=arn).get("tags", {})
            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    def _has_tag(self, item: dict, key: str) -> bool:
        return key in item

    def _get_tag(self, item: dict, key: str) -> Optional[str]:
        return item.get(key, None)

    @property
    def _client_name(self) -> str:
        return "logs"

    @property
    def _paginator(self):
        return "describe_log_groups"

    @property
    def _filters(self):
        return {}
