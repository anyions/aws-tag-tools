# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Optional, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("CloudFront")
class CloudFrontScanner(Scanner):
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
        CloudFront is global service, ensure just create one global client
        """
        super().__init__(account_id, profile=profile, regions=["global"])

    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        distributions = item.get("DistributionList", {})
        for dist_item in distributions.get("Items", []):
            arn = dist_item.get("ARN", None)
            if arn is None:
                continue

            resource_tags = client.list_tags_for_resource(Resource=arn)
            origin_value = self._get_tag(resource_tags.get("Tags", {}), key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "cloudfront"

    @property
    def _paginator(self):
        return "list_distributions"

    @property
    def _filters(self):
        return {}

    @property
    def _tags_key(self) -> str:
        return "Items"
