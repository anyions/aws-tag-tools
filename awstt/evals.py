import datetime
import logging
import math


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


def eval_expression(exp: str, env: any) -> bool:
    data = {"env": env, **_safe_list}
    try:
        return eval(exp, {"__buildin__": None}, data)
    except Exception as e:
        logger.fatal("Fail to eval expression [%s] - %s" % (exp, e))
        return False
