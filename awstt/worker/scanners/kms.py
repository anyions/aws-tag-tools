#  Copyright (c) 2024 AnyIons, All rights reserved.
#  This file is part of aws-tag-tools, released under the MIT license.
#  See the LICENSE file in the project root for full license details.

from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("KMS")
class KMSScanner(Scanner):
    def build_resource(self, client: any, key: dict) -> AWSResource:
        resource_tags = client.list_resource_tags(KeyId=key["KeyId"])
        detail = client.describe_key(KeyId=key["KeyId"])["KeyMetadata"]

        return AWSResource(
            self.category,
            self._build_arn(client, key["KeyArn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            detail,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_keys").paginate()

        for page in paginator:
            for key in page.get("Keys", []):
                resources.append(self.build_resource(client, key))

        return resources

    @property
    def _service_name(self) -> str:
        return "kms"

    @property
    def _arn_resource_type(self) -> str:
        return "key"

    @property
    def category(self) -> str:
        return "KMS"
