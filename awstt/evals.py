#  Copyright (c) 2024 AnyIons, All rights reserved.
#  This file is part of aws-tag-tools, released under the MIT license.
#  See the LICENSE file in the project root for full license details.

import datetime
import logging
import math
import re


# add any needed builtins back in
_safe_list = dict()
_safe_list["abs"] = abs
_safe_list["int"] = int
_safe_list["str"] = str
_safe_list["float"] = float
_safe_list["math"] = math
_safe_list["now"] = datetime.datetime.now
_safe_list["date"] = datetime.datetime.date
_safe_list["time"] = datetime.datetime.time
_safe_list["today"] = datetime.datetime.today
_safe_list["timedelta"] = datetime.timedelta

logger = logging.getLogger(__name__)


def eval_expression(exp: str, env: any = None, spec: any = None) -> any:
    data = {"env": env if env is not None else {}, "spec": spec if spec is not None else {}, **_safe_list}

    # noinspection PyBroadException
    try:
        raw_exp = re.search(r"^\${(.+?)}\$$", exp).group(1)

        if raw_exp.lower() in ["type", "class", "def"]:
            return raw_exp

        if any(sub in raw_exp for sub in ["import", "__import__"]):
            logger.fatal(f"Expression contains dangerous code - {exp}")

        return eval(raw_exp, data)
    except Exception as e:
        return exp
