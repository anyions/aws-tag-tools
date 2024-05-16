# -*- coding: utf-8 -*-

from typing import List, Optional

import boto3


def detect_account_id(profile: Optional[str] = None) -> str:
    session = boto3.Session(profile_name=profile)

    return session.client("sts").get_caller_identity().get("Account")


def detect_regions(regions: Optional[str]) -> List[str]:
    if regions is None:
        return []

    return [r.lower().strip() for r in regions.split(",") if len(r.strip()) > 0]


def detect_partition(partition: Optional[str]) -> str:
    if partition is None:
        return "aws"

    if partition.lower() not in ["aws", "aws-cn", "aws-us-gov"]:
        raise NotImplementedError("partition not supported")

    return partition.lower()


def detect_region(region_name: str, partition: str) -> str:
    if "global" in region_name and partition == "aws":
        return "us-east-1"

    return region_name
