# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from abc import ABC
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import boto3

from awstt.worker.registrable import Registrable
from awstt.worker.utils import detect_region


logger = logging.getLogger(__name__)


class Scanner(Registrable, ABC):
    def __init__(self, account_id: str, *, partition: str = "aws", regions: List[str], profile: Optional[str] = None):
        """
        Initialize a resource scanner for service

        :param account_id: The AWS account id used to scan
        :type account_id: str
        :param partition: The AWS partition name, can be one of `'aws' | 'aws-cn' | 'aws-us-gov'`, default to `'aws'`
        :type partition: str
        :param regions: The AWS regions to scan
        :type regions: list of str
        :param profile: The AWS credentials' profile name to used when execute as cli, default to `None`
        :type profile: str, optional
        """

        session = boto3.Session(profile_name=profile)
        if len(regions) == 0:
            regions = session.get_available_regions(self._client_name, partition_name=partition)

        self._session = session
        self._account_id = account_id
        self._partition = partition
        self._available_regions = regions
        self._clients: List[any] = [self._create_client(self._session, region=r) for r in regions]

    @property
    def available_regions(self) -> List[str]:
        return self._available_regions

    def execute(self, *, key: str, overwrite: Optional[bool] = False) -> List[Tuple[str, List[Dict[str, str]]]]:
        """
        Tag resources with key and value

        :param key: The key of tag
        :type key: str
        :param overwrite: Whether to overwrite when the key is existed, default to `False`
        :type overwrite: bool, optional
        :return: A dict contains regional resources, @see `:class:awstt.worker.scanner.TaggingResource`
        :rtype: Dict[str, List]
        """
        regional_resources = []

        for client in self._clients:
            region = detect_region(client.meta.region_name, self._partition)
            paginator = self._list_resources(client)
            for page in paginator:
                resources = self._get_resources_from_page(client, page, key, overwrite)

                regional_resources.append(
                    (
                        region,
                        [dict(arn=self._build_arn(client, res[0]), original_value=res[1]) for res in resources],
                    )
                )

        return regional_resources

    def _create_client(self, session: any, *, region: str) -> any:
        """
        A shortcut to create boto3 service client

        :param session: The boto3 session
        :param region: The AWS region of client to connect
        :return: A boto3 service client instance
        """

        # avoid s3 get_bucket_tagging takes too long time if no tags set
        config = boto3.session.Config(connect_timeout=30, retries={"max_attempts": 0})

        return session.client(self._client_name, config=config, region_name=detect_region(region, self._partition))

    def _has_tag(self, item: dict, key: str) -> bool:
        """
        A shortcut to check whether the dict item of tags contain the key

        The method **MUST** be overridden in inherited class if root element of the `item` is not a list

        :param item: A dict object contains tags
        :param key: The key to detect whether exists
        :return: True if tags contain the key, otherwise False
        """
        return any(tag["Key"] == key for tag in item.get(self._tags_key, []))

    def _get_tag(self, item: dict, key: str) -> Optional[str]:
        """
        A shortcut to get the value from the dict item of tags by the key

        The method **MUST** be overridden in inherited class iif root element of the `item` is not a list

        :param item: A dict object contains tags
        :param key: The key to get value
        :return: The tag value if the key exists, otherwise None
        """
        return next((tag["Value"] for tag in item.get(self._tags_key, []) if tag["Key"] == key), None)

    def _list_resources(self, client: any) -> Iterable[dict]:
        """
        A shortcut to list resources, used `paginator` as default

        This method **MUST** be overridden in inherited class if `paginator` is not supported to list resources

        :param client: the boto3 client to execute method
        :return: An iterable dict contains resources information
        """
        return client.get_paginator(self._paginator).paginate(**self._filters)

    def _get_resources_from_page(
        self, client: any, item: dict, key: str, overwrite: bool = False
    ) -> List[Tuple[str, Union[str, None]]]:
        """
        Get resources from a dict return from paginator resources, @see `:method:_paging_resources`

        :param client: the boto3 client to execute the paginator, can be used to get relative information
        :param item: A dict object return from paginator
        :param key: The key will be tag to, used to check whether resource tags contains the key when require overwrite
        :param overwrite: Whether to overwrite if the key already existed
        :return: A list of tuples contain resource arn and original tag value, for example:
        `[
            ("arn:aws:s3:us-east-1:1234567890:bucket/tag_existed", "original_value"),
            ("arn:aws:s3:us-east-1:1234567890:bucket/tag_not_existed", None),
        ]`
        """
        raise NotImplementedError

    def _build_arn(self, client: any, arn_or_id: str) -> str:
        """
        A shortcut to build AWS ARN string

        :param client: The boto3 client used to get the resource, contains partition and region information
        :param arn_or_id: The original string return from `_get_resources`, can be an ARN or resource id
        :return: AWS ARN string
        """
        if arn_or_id.lower().startswith("arn:"):
            return arn_or_id

        prefix = f"arn:{self._partition}:{self._client_name}:{detect_region(client.meta.region_name, self._partition)}"

        return f"{prefix}:{self._account_id}:{self._arn_resource_type}/{arn_or_id}"

    @property
    def _client_name(self) -> str:
        """
        The client name used to create boto3 client instance

        :return: A boto3 client name
        """
        raise NotImplementedError

    @property
    def _arn_resource_type(self) -> str:
        """
        The ARN resource type of current working resources

        The property will not be used when response of paginator already contains ARN

        :return: An ARN resource type string
        """
        raise NotImplementedError

    @property
    def _paginator(self) -> str:
        """
        The paginator name used to list resources

        The property may not be used when `_list_resources` is overridden

        :return: A boto3 client paginator name
        """
        raise NotImplementedError

    @property
    def _filters(self) -> Dict[str, Any]:
        """
        The filters used in pagination

        The property may not be used when `_list_resources` is overridden

        :return: A dict contains filters, default is empty
        """
        return {}

    @property
    def _tags_key(self) -> str:
        """
        The root element name of tags items, used in `_get_tag` and `_has_tag`

        The property may not affect when `_get_tag` and `_has_tag` methods are overridden in inherited class

        :return:
        """
        return "Tags"
