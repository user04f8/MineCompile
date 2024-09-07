from langcraft import *

from langcraft.base import Statement
from langcraft.serialize import CommandKeywordToken, BlockToken, ItemToken, IntToken
from langcraft.serialize_types import _SelectorBase
from langcraft.minecraft_builtins import BlockType

# general library commands (TODO add to langcraft)

type ItemType = str  # TODO

class Setblock(Statement):
    def __init__(self, pos: Pos, block: BlockType):
        super().__init__([CommandKeywordToken('setblock'), pos, BlockToken(block)])

class Give(Statement):
    def __init__(self, selector: _SelectorBase, item: ItemType, count: int | None = None, data_component_removed_defaults=None, **data_components):
        # see https://minecraft.wiki/w/Data_component_format
        tokens = [CommandKeywordToken('give'), selector, ItemToken(item, *(data_component_removed_defaults or []), **data_components)]
        if count is not None:
            tokens.append(IntToken(count))

        super().__init__(tokens)

# constants

TRAIL_ARROW_COLOR = 0xff0000


# functions

@fun
def create_trail():
    Setblock(Pos(), 'glass')


# main loops

@ticking
def test():
    with Entities('e', type='arrow', nbt=JSON(Color=TRAIL_ARROW_COLOR)) as e:
        create_trail()

# public hooks

with Namespace('give'):
    @public
    def glass_trail_arrow():
        Give(SelfEntity(), 'tipped_arrow', 64, potion_contents=JSON(custom_color=TRAIL_ARROW_COLOR))

# langcraft debug output

display_all()  # to run, do `python -m examples.special_arrows`

