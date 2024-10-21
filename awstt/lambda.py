import logging

import executor
from config import init_config


logger = logging.getLogger(__name__)


def execute(evt: any, _):
    """
    Lambda input uses dict in format of json configure.
    """

    if evt.get("action", None) is None:
        return

    config = init_config(
        dict(
            action=evt.get("action", None),
            tags=evt.get("tags", []),
            filters=evt.get("filters", []),
            resources=evt.get("resources", []),
            force=evt.get("force", False),
        )
    )

    executor.run(config)
