# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::RouteTable")
class RouteTableScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        tables = item.get("RouteTables", [])
        for table in tables:
            if overwrite is True or not self._has_tag(table, key):
                arn = self._build_arn(client, table.get("RouteTableId"))
                resources.append((arn, self._get_tag(table, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "route-table"

    @property
    def _paginator(self):
        return "describe_route_tables"
