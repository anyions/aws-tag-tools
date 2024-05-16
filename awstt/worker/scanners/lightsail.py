# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("Lightsail")
class LightsailScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        instances = item.get("instances", [])
        for instance in instances:
            if overwrite is True or not self._has_tag(instance, key):
                arn = self._build_arn(client, instance.get("arn"))
                resources.append((arn, self._get_tag(instance, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "lightsail"

    @property
    def _paginator(self):
        return "get_instances"

    @property
    def _arn_resource_type(self) -> str:
        return "Instance"

    @property
    def _tags_key(self) -> str:
        return "tags"
