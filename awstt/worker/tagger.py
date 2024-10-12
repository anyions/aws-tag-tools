import logging
import time
from typing import List

import boto3
import botocore.config

from awstt.config import Credential
from awstt.worker.types import RegionalTaggingTarget, TaggingResponse
from awstt.worker.utils import detect_region


logger = logging.getLogger(__name__)

RESOURCES_PER_REQUEST = 20  # The max limited to tag resources per request


class Tagger(object):
    def __init__(self, partition: str, credential: Credential):
        """
        Initialize a resource tagger to tag resources

        :param partition: The AWS partition of tagger
        :param credential: The AWS credential of tagger
        :type credential: Credential
        """

        session = boto3.Session(
            aws_access_key_id=credential.access_key,
            aws_secret_access_key=credential.secret_key,
            profile_name=credential.profile,
        )

        self._session = session
        self._partition = partition
        self._account_id = session.client("sts").get_caller_identity().get("Account")

    def execute(self, targets: List[RegionalTaggingTarget]) -> List[TaggingResponse]:
        """
        Tag resources use ResourceGroupsTaggingApi

        :param targets: The regional resources to apply tags
        :type targets: List[RegionalTaggingTarget]
        """

        responses = []

        for target in targets:
            logger.info(
                f"Executing resources tagging: "
                f"region - {detect_region(target.region, self._partition)}, "
                f"resources - {[res.arn for res in target.resources]}, "
                f"tags - {[t.dict() for t in target.tags]}"
            )

            # noinspection SpellCheckingInspection
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
                client_resp = client.tag_resources(
                    ResourceARNList=[c.arn for c in chunks],
                    Tags={t.key: t.value for t in target.tags},
                )

                for item in chunks:
                    status = "Success"

                    hint = client_resp.get("FailedResourcesMap", {}).get(item.arn, {}).get("ErrorMessage", None)
                    if hint:
                        status = "Failed"
                    else:
                        overwrites = []
                        for exists_tag in item.tags:
                            for tag in target.tags:
                                if exists_tag.key == tag.key and exists_tag.value != tag.value:
                                    overwrites.append(f"{tag.key}: {exists_tag.value} -> {tag.value}")
                        if len(overwrites) > 0:
                            status = "Overwrite"
                            hint = ", ".join(overwrites)

                    item_resp = TaggingResponse(
                        category=item.category,
                        arn=item.arn,
                        status=status,
                        hint=hint,
                    )
                    responses.append(item_resp)

                time.sleep(1)  # avoid throttling

            failures = len([res for res in responses if res.status == "Failed"])
            logger.info(
                f"Finished resources tagging: "
                f"region - {target.region}, "
                f"resources - {[res.arn for res in target.resources]}, "
                f"tags - {[t.dict() for t in target.tags]}, "
                f"successes - {len(target.resources) - failures}, "
                f"failures - {failures}"
            )

        return responses
