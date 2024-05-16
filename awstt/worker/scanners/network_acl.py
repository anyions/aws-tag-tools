# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List, Tuple, Union

from awstt.worker.scanner import Scanner


@Scanner.register("EC2:NetworkACL")
class NetworkACLScanner(Scanner):
    # noinspection PyUnusedLocal
    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        resources = []

        acls = item.get("NetworkAcls", [])
        for acl in acls:
            if overwrite is True or not self._has_tag(acl, key):
                arn = self._build_arn(client, acl.get("NetworkAclId"))
                resources.append((arn, self._get_tag(acl, key)))

        return resources

    @property
    def _client_name(self) -> str:
        return "ec2"

    @property
    def _paginator(self):
        return "describe_network_acls"

    @property
    def _arn_resource_type(self) -> str:
        return "network-acl"
