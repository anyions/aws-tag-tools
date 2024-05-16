# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("CloudFormation")
class CloudFormationScanner(Scanner):
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        stacks = item.get("Stacks", [])
        for stack in stacks:
            if overwrite is True or not self._has_tag(stack, key):
                arn = self._build_arn(client, stack.get("StackId", ""))
                resources.append((arn, self._get_tag(stack, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "cloudformation"

    @property
    def _arn_resource_type(self) -> str:
        return "stack"

    @property
    def _paginator(self):
        return "describe_stacks"

    @property
    def _filters(self):
        return {}
