# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("S3::Bucket")
class S3BucketScanner(Scanner):
    def _list_resources(self, client: any) -> Iterable[dict]:
        return [client.list_buckets()]

    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        buckets = item.get("Buckets", [])
        for bucket in buckets:
            name = bucket.get("Name", None)
            if name is None:
                continue

            try:
                resource_tags = client.get_bucket_tagging(Bucket=name)
            except:  # noqa E722
                resource_tags = {"TagSet": []}

            if overwrite is True or not self._has_tag(resource_tags, key):
                arn = self._build_arn(client, name)
                resources.append((arn, self._get_tag(resource_tags, key)))

        return resources

    def _build_arn(self, client: any, arn_or_id: str) -> str:
        return f"arn:aws:s3:::{arn_or_id}"

    @property
    def _client_name(self) -> str:
        return "s3"

    @property
    def _arn_resource_type(self) -> str:
        return "s3"

    @property
    def _tags_key(self) -> str:
        return "TagSet"
