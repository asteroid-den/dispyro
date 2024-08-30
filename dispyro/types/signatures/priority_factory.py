from typing import Callable

import dispyro

PriorityFactory = Callable[["dispyro.handlers.Handler", "dispyro.Router"], int]