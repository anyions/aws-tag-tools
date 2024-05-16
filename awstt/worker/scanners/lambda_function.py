# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("Lambda::Function")
class LambdaScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        for func in item.get("Functions", []):
            arn = func.get("FunctionArn", None)
            if arn is None:
                continue

            resource_tags = client.list_tags(Resource=arn).get("Tags", {})
            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    def _has_tag(self, item: dict, key: str) -> bool:
        return key in item

    def _get_tag(self, item: dict, key: str) -> Optional[str]:
        return item.get(key, None)

    @property
    def _client_name(self) -> str:
        return "lambda"

    @property
    def _paginator(self):
        return "list_functions"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "Items"
