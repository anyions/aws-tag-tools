import logging
import time
from typing import List, Union

import boto3
import botocore.config

from awstt.config import Credential
from awstt.worker.types import AWSResource, AWSResourceTag, RegionalTaggingTarget, TaggingResponse
from awstt.worker.utils import detect_region


logger = logging.getLogger(__name__)

RESOURCES_PER_REQUEST = 20  # The max limited to tag resources per request


class Tagger(object):
    def __init__(self, partition: str, credential: Credential, action="set"):
        """
        Initialize a resource tagger to tag resources

        :param partition: The AWS partition of tagger
        :type partition: str
        :param credential: The AWS credential of tagger
        :type credential: Credential
        :param action: The action of tagger, support "set" and "delete"
        :type action: str
        """

        session = boto3.Session(
            aws_access_key_id=credential.access_key,
            aws_secret_access_key=credential.secret_key,
            profile_name=credential.profile,
        )

        self._session = session
        self._partition = partition
        self._account_id = session.client("sts").get_caller_identity().get("Account")
        self._action = action

    def execute_one(self, region: str, target: AWSResource, tags: List[Union[AWSResourceTag, str]]) -> TaggingResponse:
        """
        Tag one resource use ResourceGroupsTaggingApi

        :param region: The region of resource
        :type region: str
        :param target: The resource to apply tags
        :type target: AWSResource
        :param tags: The tags to apply
        :type tags: List[AWSResourceTag]
        """
        logger.debug(
            f"Executing resource {'tagging' if self._action == 'set' else 'untagging'}: "
            f"region - {detect_region(region, self._partition)}, "
            f"resource - {target}, "
            f"tags - {[t.dict() for t in tags]}"
        )

        # noinspection SpellCheckingInspection
        client = self._session.client(
            "resourcegroupstaggingapi",
            region_name=detect_region(region, self._partition),
            config=botocore.config.Config(
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )

        if self._action == "set":
            client_resp = client.tag_resources(
                ResourceARNList=[target.arn],
                Tags={t.key: t.value for t in tags},
            )
        else:
            client_resp = client.untag_resources(
                ResourceARNList=[target.arn],
                TagKeys=tags,
            )

        hint = client_resp.get("FailedResourcesMap", {}).get(target.arn, {}).get("ErrorMessage", None)

        return TaggingResponse(
            category=target.category,
            arn=target.arn,
            status="Success" if hint is None else "Failed",
            hint=hint,
        )

    def execute(self, targets: List[RegionalTaggingTarget]) -> List[TaggingResponse]:
        """
        Tag resources use ResourceGroupsTaggingApi

        :param targets: The regional resources to apply tags
        :type targets: List[RegionalTaggingTarget]
        """

        responses = []

        for target in targets:
            logger.debug(
                f"Executing resources {'tagging' if self._action == 'set' else 'untagging'}: "
                f"region - {detect_region(target.region, self._partition)}, "
                f"resources - {[res.arn for res in target.resources]}, "
                f"tags - {[t.dict() for t in target.tags] if self._action == 'set' else target.tags}"
            )

            # noinspection SpellCheckingInspection,DuplicatedCode
            client = self._session.client(
                "resourcegroupstaggingapi",
                region_name=detect_region(target.region, self._partition),
                config=botocore.config.Config(
                    retries={"max_attempts": 3, "mode": "standard"},
                ),
            )

            if len(target.resources) == 0 or len(target.tags) == 0:
                continue

            """limit resources per request"""
            for chunks in [
                target.resources[i : i + RESOURCES_PER_REQUEST]  # noqa: E203
                for i in range(0, len(target.resources), RESOURCES_PER_REQUEST)
            ]:
                if self._action == "set":
                    client_resp = client.tag_resources(
                        ResourceARNList=[c.arn for c in chunks],
                        Tags={t.key: t.value for t in target.tags},
                    )
                else:
                    client_resp = client.untag_resources(
                        ResourceARNList=[c.arn for c in chunks],
                        TagKeys=target.tags,
                    )

                for item in chunks:
                    status = "Success"

                    hint = client_resp.get("FailedResourcesMap", {}).get(item.arn, {}).get("ErrorMessage", None)
                    if hint:
                        status = "Failed"
                    elif self._action == "set":
                        overwrites = []

                        for exists_tag in item.tags:
                            for tag in target.tags:
                                if exists_tag.key == tag.key and exists_tag.value != tag.value:
                                    overwrites.append(f"{tag.key}: {exists_tag.value} -> {tag.value}")

                        if len(overwrites) > 0:
                            status = "Overwrite"
                            hint = ", ".join(overwrites)
                    elif self._action == "unset":
                        original_tag = [t for t in item.tags if t.key in target.tags]
                        if len(original_tag) > 0:
                            hint = ", ".join([f"{t.key}: {t.value} --> <unset>" for t in original_tag])

                    item_resp = TaggingResponse(
                        category=item.category,
                        arn=item.arn,
                        status=status,
                        hint=hint,
                    )
                    responses.append(item_resp)

                time.sleep(0.3)  # avoid throttling

            failures = len([res for res in responses if res.status == "Failed"])
            logger.debug(
                f"Finished resources {'tagging' if self._action == 'set' else 'untagging'}: "
                f"region - {target.region}, "
                f"resources - {[res.arn for res in target.resources]}, "
                f"tags - {[t.dict() for t in target.tags] if self._action == 'set' else target.tags}",
                f"successes - {len(target.resources) - failures}, " f"failures - {failures}",
            )

        return responses
