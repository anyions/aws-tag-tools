# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("KMS")
class KMSScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        for key in item.get("Keys", []):
            key_arn = key.get("KeyArn", None)
            key_id = key.get("KeyId", None)
            if key_arn is None or key_id is None:
                continue

            resource_tags = client.list_resource_tags(KeyId=key_id)
            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((key_arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "kms"

    @property
    def _paginator(self):
        return "list_keys"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "Items"
