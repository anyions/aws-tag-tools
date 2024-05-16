# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("ELB")
class ELBScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        balancers = item.get("LoadBalancers", [])

        if len(balancers) == 0:
            return []

        arns = [balancer.get("LoadBalancerArn") for balancer in balancers]

        resource_tags = client.describe_tags(ResourceArns=arns)

        for tags in resource_tags:
            arn = tags.get("ResourceArn")
            origin_value = self._get_tag(tags, key)
            if overwrite or origin_value is None:
                resources.append((arn, origin_value))

        return resources

    @property
    def _client_name(self) -> str:
        return "elbv2"

    @property
    def _paginator(self):
        return "describe_load_balancers"

    @property
    def _filters(self):
        return {}
