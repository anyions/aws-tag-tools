# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("CloudTrail")
class CloudTrailScanner(Scanner):
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
        CloudTrail is global service, ensure just create one global client
        """
        super().__init__(account_id, profile=profile, regions=["global"])

    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        trails = item.get("Trails", [])
        # noinspection SpellCheckingInspection
        arns = [t.get("TrailARN") for t in trails]

        resources_tags = []
        for chunks in [arns[i : i + 20] for i in range(0, len(arns), 20)]:  # noqa: E203
            """list max 20 resources per action"""
            for page in client.get_paginator("list_tags").paginate(ResourceIdList=chunks):
                resources_tags.extend(page.get("ResourceTagList", []))

        for tags in resources_tags:
            arn = tags.get("ResourceId")
            origin_value = self._get_tag(tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "cloudtrail"

    @property
    def _arn_resource_type(self) -> str:
        return "trail"

    @property
    def _paginator(self):
        return "list_trails"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "TagsList"
