import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Union

from .evals import eval_expression


logger = logging.getLogger(__name__)


@dataclass(frozen=True, init=True, repr=True, order=True)
class Tag:
    key: str
    value: Optional[str] = ""


@dataclass(frozen=True, init=True, repr=True, order=True)
class Resource:
    target: str
    tags: List[Union[Tag, str]] = field(default_factory=list)
    filter: Optional[str] = None
    force: Optional[bool] = False

    def __post_init__(self):
        object.__setattr__(
            self, "tags", [Tag(**tag) if isinstance(tag, dict) else tag for tag in self.tags] if self.tags else []
        )


@dataclass(frozen=True, init=True, repr=True, order=True)
class Credential:
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    profile: Optional[str] = None


@dataclass(frozen=True, init=True, repr=True, order=True)
class Config:
    action: str
    force: bool = False
    filter: Optional[str] = None
    partition: Optional[str] = "aws"
    regions: Optional[List[str]] = field(default_factory=list)
    tags: List[Union[Tag, str]] = field(default_factory=list)
    resources: List[Union[str, Resource]] = field(default_factory=list)
    credential: Optional[Credential] = field(default_factory=Credential)

    def dict(self) -> Dict[str, any]:
        return asdict(self)


class ConfigError(Exception):
    pass


def init_config(data: dict) -> Config:
    env = os.environ
    env.pop("AWS_ACCESS_KEY_ID", None)
    env.pop("AWS_SECRET_ACCESS_KEY", None)
    env.pop("AWS_SESSION_TOKEN", None)
    env.pop("AWS_DEFAULT_REGION", None)
    env.pop("AWS_REGION", None)
    env.pop("AWS_PROFILE", None)

    data_str = json.dumps(data)
    for exp in re.findall(r"\${(.+)}\$", data_str):
        exp_value = eval_expression(exp, env)
        data_str = data_str.replace(f"${{{exp}}}$", str(exp_value))

    data = json.loads(data_str)

    data["action"] = data["action"].lower()
    data["partition"] = data["partition"].lower()
    data["regions"] = [r.lower() for r in data["regions"]]

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

    if config.action == "set":
        if any(x for x in config.tags if not isinstance(x, Tag)):
            raise ConfigError(f"Tags should be a list of Tag")
        for res in [r for r in config.resources if isinstance(r, Resource)]:
            if any(x for x in res.tags if not isinstance(x, Tag)):
                print([type(x) for x in res.tags if not isinstance(x, Tag)])
                raise ConfigError(f"Resource Tags should be a list of Tag - {res}")

    if config.action == "unset":
        if any(x for x in config.tags if isinstance(x, Tag)):
            raise ConfigError(f"Tags should be a list of key str or key selector in JMESPath expression")
        for res in [r for r in config.resources if isinstance(r, Resource)]:
            if any(x for x in res.tags if isinstance(x, Tag)):
                raise ConfigError(
                    f"Resource Tags should be a list of key str or key selector in JMESPath expression - {res}"
                )
