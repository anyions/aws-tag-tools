from __future__ import annotations

import logging
import traceback
from abc import ABC, abstractmethod
from typing import List

import boto3

from awstt.config import Credential
from awstt.worker.registrable import Registrable
from awstt.worker.types import AWSResource, ResourceFilter
from awstt.worker.utils import detect_region, filter_resources, is_arn, parse_arn


logger = logging.getLogger(__name__)


class Scanner(Registrable, ABC):
    def __init__(self, partition: str, regions: List[str], credential: Credential):
        """
        Initialize a resource scanner to scan resources

        :param partition: The AWS partition of scanner
        :param regions: The AWS regions of scanner
        :param credential: The AWS credential of scanner
        :type credential: Credential
        """

        session = boto3.Session(
            aws_access_key_id=credential.access_key,
            aws_secret_access_key=credential.secret_key,
            profile_name=credential.profile,
        )

        self._session = session
        self._partition = partition
        self._available_regions = regions
        self._account_id = None

    def is_supported_arn(self, arn: str) -> bool:
        info = parse_arn(arn)
        return info.service == self._service_name and info.resource_type == self._arn_resource_type

    def execute(self, *, filters: list[ResourceFilter]) -> List[AWSResource]:
        """
        Scan resources with selectors

        :param filters: The selectors to filter resources
        :return: A list ARNs of resources matched selectors
        :rtype: List[AWSResource]
        """
        logger.debug(f"Starting resources scan - {self.category}")

        # init account_id only when executing, make faster
        self._account_id = self._session.client("sts").get_caller_identity()["Account"]

        # init regions only when executing, make faster
        if len(self._available_regions) == 0:
            self._available_regions = self._session.get_available_regions(
                self._service_name, partition_name=self._partition
            )

        resources: List[AWSResource] = []
        for region in self._available_regions:
            try:
                logger.debug(f"Scanning - {self.category} @ {region}")
                client = self._create_client(self._session, region=detect_region(region, self._partition))
                founded = self._list_resources(client)
                filtered = filter_resources(founded, filters)

                resources.extend(filtered)
                logger.debug(
                    f"Finished - {self.category} @ {region}, " f"total - {len(founded)}, matched - {len(filtered)}"
                )
            except Exception as e:
                stack = f"stack:\n{traceback.format_exc()}" if logger.isEnabledFor(logging.DEBUG) else ""
                logger.error(f"Failed - {self.category} @ {region}, error: {e} {stack}")

        logger.debug(f"Finished resources scan - {self.category}, found - {len(resources)}")

        return resources

    def _create_client(self, session: any, *, region: str) -> any:
        """
        A shortcut to create boto3 service client

        :param session: The boto3 session
        :param region: The AWS region of client to connect
        :return: A boto3 service client instance
        """

        # avoid s3 get_bucket_tagging takes too long time if no tags set
        # config = boto3.session.Config(connect_timeout=30, retries={"max_attempts": 0})

        return session.client(self._service_name, region_name=region)

    def _build_arn(self, client: any, arn_or_id: str) -> str:
        """
        A shortcut to build AWS ARN string for most Services

        :param client: The boto3 client used to get the resource, contains partition and region information
        :param arn_or_id: The original string return from `_get_resources`, can be an ARN or resource id
        :return: AWS ARN string
        """
        if is_arn(arn_or_id):
            return arn_or_id

        prefix = (
            f"arn:{self._partition}:{self._arn_service_type}:{detect_region(client.meta.region_name, self._partition)}"
        )

        return f"{prefix}:{self._account_id}:{self._arn_resource_type}/{arn_or_id}"

    @abstractmethod
    def _list_resources(self, client: any) -> List[AWSResource]:
        """
        list resources in region with filters

        :param client: A boto3 client
        :return: A list ARNs of resources matched filters
        :rtype: List[AWSResource]
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def _service_name(self) -> str:
        """
        The service name used to create boto3 client instance

        :return: A boto3 client service name
        """
        raise NotImplementedError

    @property
    def _arn_service_type(self) -> str:
        """
        The ARN service type to detect or build ARN, default is the same as `_service_name`

        :return: An ARN service type string
        """
        return self._service_name

    @property
    @abstractmethod
    def _arn_resource_type(self) -> str:
        """
        The ARN resource type to detect or build ARN

        :return: An ARN resource type string
        """
        return ""

    @property
    @abstractmethod
    def category(self) -> str:
        """
        The name of resource scanner

        :return: Scanner name
        """
        raise NotImplementedError

    @property
    def arn_pattern(self) -> str:
        """
        The ARN pattern of resource scanner

        :return: Scanner ARN pattern
        """
        return f"arn:{self._partition}:{self._arn_service_type}:*:*:{self._arn_resource_type}/*"
