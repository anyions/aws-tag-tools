from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EFS")
class EFSScanner(Scanner):
    def build_resource(self, client: any, fs: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, fs["FileSystemArn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in fs.get("Tags", [])],
            fs,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_file_systems").paginate()

        for page in paginator:
            for fs in page.get("FileSystems", []):
                resources.append(self.build_resource(client, fs))

        return resources

    @property
    def _service_name(self) -> str:
        return "efs"

    @property
    def _arn_service_type(self) -> str:
        # noinspection SpellCheckingInspection
        return "elasticfilesystem"

    @property
    def _arn_resource_type(self) -> str:
        return "file-system"

    @property
    def category(self) -> str:
        return "EFS"
