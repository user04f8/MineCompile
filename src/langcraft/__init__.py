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
from .dimension import *

def init(namespace=None):
    if namespace:
        Namespace(namespace).__enter__()
        with OnLoadFun():
            DebugStatement(f'langcraft datapack "{namespace}" ON', include_selector=False)
    else:
        with OnLoadFun():
            DebugStatement(f'langcraft datapack ON', include_selector=False)
