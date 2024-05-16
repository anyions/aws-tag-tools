# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::InternetGateway")
class InternetGatewayScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        gateways = item.get("InternetGateways", [])
        for gateway in gateways:
            if overwrite is True or not self._has_tag(gateway, key):
                arn = self._build_arn(client, gateway.get("InternetGatewayId", ""))
                resources.append((arn, self._get_tag(gateway, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "internet-gateway"

    @property
    def _paginator(self):
        return "describe_internet_gateways"

    @property
    def _filters(self):
        return {}
