import logging
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Union


logger = logging.getLogger(__name__)


@dataclass(frozen=True, init=True, repr=True, order=True)
class Tag:
    key: str
    value: Optional[str] = ""


@dataclass(frozen=True, init=True, repr=True, order=True)
class Resource:
    target: str
    tags: List[Tag] = field(default_factory=list)
    selector: Optional[str] = None
    force: Optional[bool] = False


@dataclass(frozen=True, init=True, repr=True, order=True)
class Credential:
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    profile: Optional[str] = None


@dataclass(frozen=True, init=True, repr=True, order=True)
class Config:
    action: str
    force: bool = False
    selector: Optional[str] = None
    partition: Optional[str] = "aws"
    regions: Optional[List[str]] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
    resources: List[Union[str, Resource]] = field(default_factory=list)
    credential: Optional[Credential] = field(default_factory=Credential)

    def dict(self) -> Dict[str, any]:
        return asdict(self)


class ConfigError(Exception):
    pass


def init_config(data: dict) -> Config:
    data["credential"] = Credential(**data["credential"])
    data["resources"] = (
        [Resource(**res) if isinstance(res, dict) else res for res in data["resources"]] if data["resources"] else []
    )
    data["tags"] = [Tag(**tag) if isinstance(tag, dict) else tag for tag in data["tags"]] if data["tags"] else []

    return Config(**data)


def check_config(config: Config):
    if config.credential.profile is not None and (
        config.credential.access_key is not None or config.credential.secret_key is not None
    ):
        raise ConfigError("Only one of credential.profile or credential.access_key/secret_key should be provided")

    if config.credential.profile is None and (
        config.credential.access_key is None or config.credential.secret_key is None
    ):
        raise ConfigError("Either credential.profile or both credential.access_key/secret_key should be provided")
