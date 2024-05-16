# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::Subnet")
class SubnetScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        subnets = item.get("Subnets", [])
        for subnet in subnets:
            if overwrite is True or not self._has_tag(subnet, key):
                arn = self._build_arn(client, subnet.get("SubnetId"))
                resources.append((arn, self._get_tag(subnet, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _paginator(self):
        return "describe_subnets"

    @property
    def _arn_resource_type(self) -> str:
        return "subnet"
