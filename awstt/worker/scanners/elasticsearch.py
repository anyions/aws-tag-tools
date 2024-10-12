from typing import List

from awstt.worker.scanner import Scanner
from awstt.worker.types import AWSResource, AWSResourceTag


@Scanner.register("Elasticsearch:Domain")
class ElasticsearchScanner(Scanner):
    def build_resource(self, client: any, domain: dict) -> AWSResource:
        arn = domain["ARN"]
        resource_tags = client.list_tags(ARN=arn)

        return AWSResource(
            self.category,
            self._build_arn(client, arn),
            [AWSResourceTag(tag["Key"], tag["Value"]) for tag in resource_tags.get("Tags", [])],
            domain,
        )

    def _list_resources(self, client: any) -> List[AWSResource]:
        resources = []

        domains = client.list_domain_names(EngineType="Elasticsearch").get("DomainNames", [])
        if len(domains) == 0:
            return []

        paginator = [client.describe_elasticsearch_domains(DomainNames=[d.get("DomainName") for d in domains])]

        for page in paginator:
            for domain in page.get("DomainStatusList", []):
                resources.append(self.build_resource(client, domain))

        return resources

    @property
    def _service_name(self) -> str:
        return "es"

    @property
    def _arn_resource_type(self) -> str:
        return "domain"

    @property
    def category(self) -> str:
        return "Elasticsearch:Domain"
