from langcraft import *

from langcraft.base import Statement
from langcraft.serialize import CommandKeywordToken, BlockToken
from langcraft.minecraft_builtins import BlockType

# general library commands (TODO add to langcraft)

class Setblock(Statement):
    def __init__(self, pos: Pos, block: BlockType):
        super().__init__([CommandKeywordToken('setblock'), pos, BlockToken(block)])


# constants

TRAIL_ARROW_COLOR = 0xff0000


# functions

@fun
def create_trail():
    Setblock(Pos(), 'glass')


# public hooks

@public
def test():
    with Entities('e', type='arrow', nbt=JSON(Color=TRAIL_ARROW_COLOR)) as e:
        create_trail()


# langcraft debug output

display_all()  # to run, do `python -m examples.special_arrows`