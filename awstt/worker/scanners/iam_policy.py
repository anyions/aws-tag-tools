from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("IAM:Policy")
class IAMPolicyScanner(Scanner):
    def __init__(self, partition, _, credential):
        if partition in ["aws", "aws-gov"]:
            super().__init__(partition, ["global"], credential)
        else:
            super().__init__(partition, ["cn-northwest-1", "cn-northeast-1"], credential)

    def build_resource(self, client: any, policy: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, policy["Arn"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in policy.get("Tags", [])],
            policy,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("list_policies").paginate(**{"Scope": "Local"})

        for page in paginator:
            for policy in page.get("Policies", []):
                resources.append(self.build_resource(client, policy))

        return resources

    @property
    def _service_name(self) -> str:
        return "iam"

    @property
    def _arn_resource_type(self) -> str:
        return "policy"

    @property
    def category(self) -> str:
        return "IAM:Policy"
