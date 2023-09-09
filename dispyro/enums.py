from enum import Enum, auto


class RunLogic(Enum):
    ONE_RUN_PER_EVENT = auto()
    ONE_RUN_PER_ROUTER = auto()
    UNLIMITED = auto()


class ExpectedConditionCheckType(Enum):
    ITER_ALL_ROUTERS = auto()
    PUT_ACTUAL_ROUTER = auto()
