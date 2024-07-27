from typing import List

from .commands import RawCommand
from .base import Namespace, OnLoadFun, Debug
from .globals import Setup, ScoreSetup
from .debug_utils import print_warn

def legacy_init(namespace=None):
    if namespace:
        Namespace(namespace).__enter__()
        with OnLoadFun():
            Debug(f'langcraft datapack "{namespace}" ON', include_selector=False)
    else:
        with OnLoadFun():
            Debug(f'langcraft datapack ON', include_selector=False)

def load(setups: List[Setup]):
    with OnLoadFun():
        for setup in setups:
            if isinstance(setup, ScoreSetup):
                RawCommand
            else:
                print_warn(f'UNKOWN SETUP INSTRUCTION {setup}')
        Debug(f'load complete', include_selector=False)
    

