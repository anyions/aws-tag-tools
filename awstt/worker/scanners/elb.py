from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("ELB")
class ELBScanner(Scanner):
    def build_resource(self, client: any, lb: dict) -> AWSResource:
        arn = lb.get("LoadBalancerArn")
        resource_tags = []
        for page in client.describe_tags(ResourceArns=[arn]):
            for item in page.get("TagDescriptions", []):
                resource_tags.extend(item.get("Tags", []))

        return AWSResource(
            self.category,
            self._build_arn(client, lb["InstanceId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags],
            lb,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_load_balancers").paginate()

        for page in paginator:
            for lb in page.get("LoadBalancers", []):
                resources.append(self.build_resource(client, lb))

        return resources

    @property
    def _service_name(self) -> str:
        return "elbv2"

    @property
    def _arn_service_type(self) -> str:
        return "elasticloadbalancing"

    @property
    def _arn_resource_type(self) -> str:
        return "loadbalancer"

    @property
    def category(self) -> str:
        return "ELB"
