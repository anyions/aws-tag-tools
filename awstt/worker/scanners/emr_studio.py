from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EMR:Studio")
class EMRStudioScanner(Scanner):
    def build_resource(self, client: any, studio: dict) -> AWSResource:
        detail = client.describe_studio(StudioId=studio.get("Id")).get("Studio", {})

        return AWSResource(
            self.category,
            self._build_arn(client, detail.get("StudioArn")),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in detail.get("Tags", [])],
            detail,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_studios").paginate()

        for page in paginator:
            for studio in page.get("Studios", []):
                resources.append(self.build_resource(client, studio))

        return resources

    @property
    def _service_name(self) -> str:
        return "emr"

    @property
    def _arn_resource_type(self) -> str:
        return "studio"

    @property
    def category(self) -> str:
        return "EMR:Studio"
