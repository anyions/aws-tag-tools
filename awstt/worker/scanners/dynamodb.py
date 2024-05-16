# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("DynamoDB")
class DynamoDBScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        tables = item.get("TableNames", [])

        for table in tables:
            arn = self._build_arn(client, table)

            resource_tags = {self._tags_key: []}
            for page in client.get_paginator("list_tags_of_resource").paginate(ResourceArn=arn):
                resource_tags[self._tags_key].extend(page.get(self._tags_key, []))

            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "dynamodb"

    @property
    def _arn_resource_type(self) -> str:
        return "table"

    @property
    def _paginator(self):
        return "list_tables"

    @property
    def _filters(self):
        return {}
