# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2::AMI")
class AMIScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        images = item.get("Images", [])
        for image in images:
            if overwrite is True or not self._has_tag(image, key):
                arn = self._build_arn(client, image.get("ImageId", ""))
                resources.append((arn, self._get_tag(image, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "image"

    @property
    def _paginator(self):
        return "describe_images"

    @property
    def _filters(self):
        return {"Owners": ["self"]}
