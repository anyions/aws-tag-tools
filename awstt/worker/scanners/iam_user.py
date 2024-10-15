from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("IAM:User")
class IAMUserScanner(Scanner):
    def __init__(self, partition, _, credential):
        if partition in ["aws", "aws-gov"]:
            super().__init__(partition, ["global"], credential)
        else:
            super().__init__(partition, ["cn-northwest-1", "cn-northeast-1"], credential)

    def build_resource(self, client: any, user: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, user["Arn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in user.get("Tags", [])],
            user,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_users").paginate()

        for page in paginator:
            for user in page.get("Users", []):
                resources.append(self.build_resource(client, user))

        return resources

    @property
    def _service_name(self) -> str:
        return "iam"

    @property
    def _arn_resource_type(self) -> str:
        return "user"

    @property
    def category(self) -> str:
        return "IAM:User"
