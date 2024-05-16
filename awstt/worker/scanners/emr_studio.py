# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EMR::Studio")
class EMRStudioScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        studios = item.get("Studios", [])
        for studio in studios:
            studio_id = studio.get("StudioId", None)
            if studio_id is None:
                continue

            detail = client.describe_studio(StudioId=studio_id).get("Studio", {})
            if overwrite or not self._has_tag(detail, key):
                resources.append((detail.get("StudioArn"), self._get_tag(detail, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "emr"

    @property
    def _paginator(self):
        return "list_studios"

    @property
    def _filters(self):
        return {}
