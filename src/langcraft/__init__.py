from .dimension import CustomDimensionType, CustomDimension
from .json_utils import JSONtemplate, JSON, FunctionJSON

from .serialize_types import Objective, Pos, Rot, ExternalResourceLocation, Dimension 
from .scores import Score
from .load import legacy_init
from .base import Namespace, Pathspace, Statement, Pass, Debug, Fun, Partial, fun, ticking, on_load, public, metafun, lambda_metafun

from .mutables import Entities, SingleEntity, SelfEntity
from .control_flow import If, While, Do, Schedule, ScoreTree
from .commands import Condition, Advancement, Teleport, Kill
from .globals import GLOBALS
from .compile import compile_all, compile_program
from .debug import display, display_all

from sys import argv

# python -m langcraft build
if __name__ == 'langcraft' and len(argv) > 1 and argv[1] == 'build':
    from .autogen.commands import _autogen
    _autogen()

import langcraft.autogened_commands as cmd
