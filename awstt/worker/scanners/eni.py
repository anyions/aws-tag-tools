# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::ENI")
class ENIScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        interfaces = item.get("NetworkInterfaces", [])
        for interface in interfaces:
            if overwrite is True or not self._has_tag(interface, key):
                arn = self._build_arn(client, interface.get("NetworkInterfaceId"))
                resources.append((arn, self._get_tag(interface, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "network-interface"

    @property
    def _paginator(self):
        return "describe_network_interfaces"

    @property
    def _tags_key(self) -> str:
        return "TagSet"
