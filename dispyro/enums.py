from enum import Enum, auto


class RunLogic(Enum):
    ONE_RUN_PER_EVENT = auto()
    ONE_RUN_PER_ROUTER = auto()
    UNLIMITED = auto()


class MiddlewareState(Enum):
    UNACTIVE = auto()
    CALLED_ENTER = auto()
    CALLED_EXIT = auto()