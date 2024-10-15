import re
from datetime import date, datetime, time, timedelta
from json import JSONDecoder, JSONEncoder
from typing import List, Tuple

import jmespath
from dateutil import parser

from awstt.worker.types import ArnInfo, AWSResource, ResourceFilter


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


def is_arn_wild_match(pattern: str, inputs: str) -> bool:
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

    return matched


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


def filter_resources(resources: List[AWSResource], filters: List[ResourceFilter]) -> List[AWSResource]:
    if len(filters) == 0:
        return resources

    matched_list = []
    for res in resources:
        matched = False
        for f in filters:
            if is_arn(f.pattern) and not is_arn_wild_match(f.pattern, res.arn):
                continue

            if not is_arn(f.pattern) and f.pattern.lower() != res.category.lower():
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


def filter_tags(resources: List[AWSResource], filters: List[str]) -> List[Tuple[AWSResource, List[str]]]:
    if len(filters) == 0:
        return []

    resources_with_filtered_tags = []

    for resource in resources:
        tags: List[str] = []

        for f in filters:
            if f == "*":
                tags.extend([t.key for t in resource.tags])
                continue

            if not f.lower().startswith("tags["):
                f = f"tags[?key=='{f}']"

            ts = jmespath.search(f, resource.dict())

            if ts is None:
                continue
            elif isinstance(ts, list) and len(ts) > 0:
                if isinstance(ts[0], str):
                    tags.extend(ts)
                elif isinstance(ts[0], dict) is not None:
                    tags.extend([t["key"] for t in ts if t.get("Key", None) is not None])
            elif isinstance(ts, dict) and ts.get("key", None) is not None:
                tags.append(ts["key"])
            elif isinstance(ts, str):
                tags.append(ts)

        if len(tags) > 0:
            resources_with_filtered_tags.append((resource, tags))

    return resources_with_filtered_tags


def detect_region(region_name: str, partition: str) -> str:
    if region_name == "" or "global" in region_name:
        if partition == "aws":
            return "us-east-1"
        if partition == "aws-gov":
            return "us-gov"

    return region_name
