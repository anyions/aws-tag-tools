# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::VPNGateway")
class VPNGatewayScanner(Scanner):
    def _list_resources(self, client: any) -> Iterable[dict]:
        return [client.describe_vpn_gateways()]

    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        gateways = item.get("VpnGateways", [])
        for gateway in gateways:
            if overwrite is True or not self._has_tag(gateway, key):
                arn = self._build_arn(client, gateway.get("VpnGatewayId"))
                resources.append((arn, self._get_tag(gateway, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "vpn-gateway"
