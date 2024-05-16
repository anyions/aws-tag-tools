# -*- coding: utf-8 -*-

import logging
import time
from typing import Dict, List, NotRequired, Optional, TypedDict

import boto3

from awstt.worker.utils import detect_region


logger = logging.getLogger(__name__)

RESOURCES_PER_REQUEST = 20  # The max limited to tag resources per request


class TaggingResource(TypedDict):
    arn: str
    original_value: NotRequired[str]


class Tagger(object):
    def __init__(self, account_id: str, *, partition: str = "aws", profile: Optional[str] = None):
        """
        Initialize a resource tagger to tag resources

        :param account_id: The AWS account id used to tag resources
        :type account_id: str
        :param partition: The AWS partition name, can be one of `'aws' | 'aws-cn' | 'aws-us-gov'`, default to `'aws'`
        :type partition: str
        :param profile: The profile name of AWS credentials used when execute as cli, default to `None`
        :type profile: str, optional
        """

        self._account_id = account_id
        self._partition = partition
        self._profile = profile

    def execute(self, *, key: str, value: str, regional_resources: Dict[str, List[TaggingResource]]):
        """
        Tag resources use ResourceGroupsTaggingApi

        :param regional_resources: The regional resources to be tagging
        :type regional_resources: Dict[str, List[TaggingResource]]
        :param key: The key of tag
        :type key: str
        :param value: The value of tag
        :type value: str
        """
        for region, resources in regional_resources.items():
            session = boto3.Session(profile_name=self._profile)
            # noinspection SpellCheckingInspection
            tagger = session.client(
                "resourcegroupstaggingapi",
                region_name=detect_region(region, self._partition),
            )

            if len(resources) == 0:
                continue

            for chunks in [
                resources[i : i + RESOURCES_PER_REQUEST]  # noqa: E203
                for i in range(0, len(resources), RESOURCES_PER_REQUEST)
            ]:
                """tag max 20 resources per action"""
                resp = tagger.tag_resources(ResourceARNList=[c.get("arn") for c in chunks], Tags={key: value})

                for res in chunks:
                    arn = res.get("arn")
                    original_value = res.get("original_value", None)

                    logger.info(
                        "resource tagged - %s",
                        dict(
                            resource=arn,
                            status=arn not in resp,
                            original_value=original_value,
                            error=resp.get(arn, {}).get("ErrorMessage", None),
                        ),
                    )

                time.sleep(1)  # avoid throttling
