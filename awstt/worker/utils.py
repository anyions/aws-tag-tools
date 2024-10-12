import re
from datetime import date, datetime, time, timedelta
from json import JSONDecoder, JSONEncoder
from typing import List

import jmespath
from dateutil import parser

from awstt.worker.types import ArnInfo, AWSResource, ResourceSelector


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return (datetime.min + obj).time().isoformat()

        return super(DateTimeEncoder, self).default(obj)


class DateTimeDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(d):
        for key, value in d.items():
            try:
                d[key] = parser.parse(value)
            except (ValueError, AttributeError):
                pass
        return d


def is_arn(inputs: str) -> bool:
    return inputs.lower().startswith("arn:")


def is_arn_wild_match(pattern: str, inputs: str) -> (bool, bool):
    self = parse_arn(pattern)
    other = parse_arn(inputs)

    matched = (
        self.partition == other.partition
        and self.service == other.service
        and (self.region == other.region or self.region in ["*", ""] or other.region in ["*", ""])
        and (self.account_id == other.account_id or self.account_id in ["*", ""] or other.account_id in ["*", ""])
        and self.resource_type == other.resource_type
        and (self.resource == other.resource or self.resource in ["*", ""] or other.resource in ["*", ""])
    )

    wild = self.region in ["*", ""] or self.account_id in ["*", ""] or self.resource in ["*", ""]

    return matched, wild


def parse_arn(inputs: str) -> ArnInfo:
    pattern = (
        r"^arn:(?P<Partition>[^:\n]*)"
        r":(?P<Service>[^:\n]*)"
        r":(?P<Region>[^:\n]*)"
        r":(?P<AccountID>[^:\n]*)"
        r":(?P<Ignore>(?P<ResourceType>[^:\/\n]*)[:\/])?(?P<Resource>.*)$"
    )

    m = re.match(pattern, inputs, re.IGNORECASE)

    return ArnInfo(
        m.group("Partition"),
        m.group("Service"),
        m.group("Region"),
        m.group("AccountID"),
        m.group("ResourceType"),
        m.group("Resource"),
    )


def filter_resources(resources: List[AWSResource], filters: List[ResourceSelector]) -> List[AWSResource]:
    if len(filters) == 0:
        return resources

    matched_list = []
    for res in resources:
        matched = False
        for f in filters:
            if not is_arn_wild_match(f.arn_pattern, res.arn):
                continue

            if len(f.conditions) == 0:
                matched = True
                break

            for cond in f.conditions:
                met = jmespath.search(cond, res.dict())
                if isinstance(met, bool) and met:
                    matched = True
                elif isinstance(met, list) and len(met) > 0:
                    matched = True
                elif met:
                    matched = True
                else:
                    matched = False

        if matched:
            if not any(res.arn == m.arn for m in matched_list):
                matched_list.append(res)

    return matched_list


def detect_region(region_name: str, partition: str) -> str:
    if (region_name == "" or "global" in region_name) and partition == "aws":
        return "us-east-1"

    return region_name
