from dataclasses import asdict, dataclass
from typing import Dict, List, Union


@dataclass(frozen=True, init=True, repr=True, order=True)
class _BaseType:
    def dict(self) -> Dict[str, any]:
        return asdict(self)


@dataclass(frozen=True, init=True, repr=True, order=True)
class ArnInfo(_BaseType):
    partition: str
    service: str
    region: str
    account_id: str
    resource_type: str
    resource: str


@dataclass(frozen=True, init=True, repr=True, order=True)
class AWSResourceTag(_BaseType):
    key: str
    value: str


@dataclass(frozen=True, init=True, repr=True, order=True)
class AWSResource(_BaseType):
    category: str
    arn: str
    tags: List[AWSResourceTag]
    spec: dict


@dataclass(frozen=True, init=True, repr=True, order=True)
class ResourceFilter(_BaseType):
    pattern: str
    conditions: List[str]


@dataclass(frozen=True, init=True, repr=True, order=True)
class RegionalTaggingTarget(_BaseType):
    region: str
    resources: List[AWSResource]
    tags: List[Union[AWSResourceTag, str]]


@dataclass(frozen=True, init=True, repr=True, order=True)
class TaggingResponse(_BaseType):
    category: str
    arn: str
    status: str
    hint: str = None
