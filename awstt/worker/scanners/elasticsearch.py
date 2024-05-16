# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("Elasticsearch")
class ElasticsearchScanner(Scanner):
    def _list_resources(self, client: any) -> Iterable[dict]:
        domains = client.list_domain_names(EngineType="Elasticsearch").get("DomainNames", [])
        if len(domains) == 0:
            return []

        return [client.describe_elasticsearch_domains(DomainNames=[d.get("DomainName") for d in domains])]

    # noinspection PyUnusedLocal, DuplicatedCode
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        domains = item.get("DomainStatusList", [])
        for domain in domains:
            arn = domain.get("ARN", None)
            if arn is None:
                continue

            resource_tags = client.list_tags(ARN=arn)
            origin_value = self._get_tag(resource_tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "es"

    @property
    def _tags_key(self) -> str:
        return "TagList"
