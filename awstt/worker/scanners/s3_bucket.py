from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("S3:Bucket")
class S3BucketScanner(Scanner):
    def build_resource(self, client: any, bucket: dict) -> AWSResource:
        # noinspection PyBroadException
        try:
            resource_tags = client.get_bucket_tagging(Bucket=bucket["Name"])
        except:  # noqa: E722
            resource_tags = {"TagSet": []}

        return AWSResource(
            self.category,
            self._build_arn(client, bucket["Name"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("TagSet", [])],
            bucket,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_buckets").paginate()

        for page in paginator:
            for bucket in page.get("Buckets", []):
                if client.get_bucket_location(Bucket=bucket["Name"])["LocationConstraint"] == client.meta.region_name:
                    resources.append(self.build_resource(client, bucket))

        return resources

    def _build_arn(self, client: any, bucket_name: str) -> str:
        return f"arn:aws:s3:::{bucket_name}"

    @property
    def _service_name(self) -> str:
        return "s3"

    @property
    def _arn_resource_type(self) -> str:
        return ""

    @property
    def category(self) -> str:
        return "S3:Bucket"
