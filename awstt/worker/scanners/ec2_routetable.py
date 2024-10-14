from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:RouteTable")
class RouteTableScanner(Scanner):
    def _build_resource(self, client: any, table: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, table["RouteTableId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in table.get("Tags", [])],
            table,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_route_tables").paginate()

        for page in paginator:
            for table in page.get("RouteTables", []):
                resources.append(self._build_resource(client, table))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "route-table"

    @property
    def category(self) -> str:
        return "EC2:RouteTable"
