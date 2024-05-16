# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("IAM::Role")
class IAMRoleScanner(Scanner):
    # noinspection PyUnusedLocal
    def __init__(
        self,
        account_id: str,
        *,
        partition: str = "aws",
        regions: Optional[List[str]] = None,
        profile: Optional[str] = None,
    ):
        """
        IAM is global service, ensure just create one global client
        """
        super().__init__(account_id, profile=profile, regions=["global"])

    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        roles = item.get("Roles", [])
        for role in roles:
            resource_tags = {self._tags_key: []}
            tags_paginator = client.get_paginator("list_role_tags").paginate(RoleName=role.get("RoleName"))
            # noinspection DuplicatedCode
            for page in tags_paginator:
                resource_tags[self._tags_key].extend(page.get(self._tags_key, []))

            if overwrite is True or not self._has_tag(resource_tags, key):
                resources.append((role.get("Arn"), self._get_tag(resource_tags, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "iam"

    @property
    def _paginator(self):
        return "list_roles"

    @property
    def _filters(self):
        return {}
