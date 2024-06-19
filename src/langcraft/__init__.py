from .serialize import *
from .json_utils import *
from .globals import *
from .base import *
from .compile import *
from .debug import *
from .control_flow import *
from .commands import *
from .types import *
from .mutables import *

with OnLoadFun():
    DebugStatement('langcraft datapack ON', include_selector=False)
