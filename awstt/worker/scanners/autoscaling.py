# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::AutoScalingGroup")
class AutoScalingScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        groups = item.get("AutoScalingGroups", [])
        for group in groups:
            if overwrite is True or not self._has_tag(group, key):
                arn = group.get("AutoScalingGroupARN")
                resources.append((arn, self._get_tag(group, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "autoscaling"

    @property
    def _paginator(self):
        return "describe_auto_scaling_groups"

    @property
    def _filters(self):
        return {}
