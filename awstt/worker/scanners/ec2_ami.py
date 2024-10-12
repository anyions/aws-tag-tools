from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("EC2:AMI")
class AMIScanner(Scanner):
    def build_resource(self, client: any, image: dict) -> AWSResource:
        return AWSResource(
            self.category,
            self._build_arn(client, image["ImageId"]),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in image.get("Tags", [])],
            image,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []
        paginator = client.get_paginator("describe_images").paginate(**{"Owners": ["self"]})

        for page in paginator:
            for image in page.get("Images", []):
                resources.append(self.build_resource(client, image))

        return resources

    @property
    def _service_name(self) -> str:
        return "ec2"

    @property
    def _arn_resource_type(self) -> str:
        return "image"

    @property
    def category(self) -> str:
        return "EC2:AMI"
