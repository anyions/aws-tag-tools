# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::EIP")
class EIPScanner(Scanner):
    def _list_resources(self, client: any) -> Iterable[dict]:
        return [client.describe_addresses()]

    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        addresses = item.get("Addresses", [])
        for address in addresses:
            if overwrite is True or not self._has_tag(address, key):
                arn = self._build_arn(client, address.get("AllocationId"))
                resources.append((arn, self._get_tag(address, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "eip"
