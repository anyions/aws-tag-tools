# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2")
class EC2Scanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        reservations = item.get("Reservations", [])
        for reservation in reservations:
            instances = reservation.get("Instances", [])
            for instance in instances:
                if overwrite is True or not self._has_tag(instance, key):
                    arn = self._build_arn(client, instance.get("InstanceId", ""))
                    resources.append((arn, self._get_tag(instance, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "instance"

    @property
    def _paginator(self):
        return "describe_instances"

    @property
    def _filters(self):
        return {}
