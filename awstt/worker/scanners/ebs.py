# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::EBS")
class EBSScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        volumes = item.get("Volumes", [])
        for volume in volumes:
            if overwrite is True or not self._has_tag(volume, key):
                arn = self._build_arn(client, volume.get("VolumeId", ""))
                resources.append((arn, self._get_tag(volume, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "image"

    @property
    def _paginator(self):
        return "describe_volumes"

    @property
    def _filters(self):
        return {}
