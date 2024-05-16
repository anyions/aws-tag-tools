# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::VPCPeering")
class VPCPeeringScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        vpcs = item.get("VpcPeeringConnections", [])
        for vpc in vpcs:
            if overwrite is True or not self._has_tag(vpc, key):
                arn = self._build_arn(client, vpc.get("VpcPeeringConnectionId"))
                resources.append((arn, self._get_tag(vpc, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _paginator(self):
        return "describe_vpc_peering_connections"

    @property
    def _arn_resource_type(self) -> str:
        return "vpc-peering-connection"
