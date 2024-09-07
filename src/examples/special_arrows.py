from langcraft import *

from langcraft.base import Statement
from langcraft.serialize import CommandKeywordToken, BlockToken, ItemToken, IntToken
from langcraft.serialize_types import _SelectorBase
from langcraft.minecraft_builtins import BlockType

# to run, do `python -m examples.special_arrows`

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

# actual test code

class SpecialArrow(type):
    def __new__(cls, name, bases, class_dict):
        # Extract the COLOR from the class being defined
        color = class_dict.get('COLOR')

        with Pathspace('arrows'):
            # Define the ticking function to handle arrows with the specified color
            @ticking
            def on_tick():
                with Entities('e', type='arrow', nbt=JSON(item=JSON(components=JSON(**{'"minecraft:potion_contents"': JSON(custom_color=color)})))) as e:
                    class_dict.get('every_tick')()

        # Define the public hook to give arrows with the specified color
        with Namespace('give'):
            @public
            def give_trail_arrow():
                Give(SelfEntity(), 'tipped_arrow', 64, potion_contents=JSON(custom_color=color))

        # Call the parent's __new__ method to create the class
        return super().__new__(cls, name, bases, class_dict)
    
class GlassTrailArrow(metaclass=SpecialArrow):
    COLOR = 0xcccccc

    def every_tick():
        Setblock(Pos.relative(y=-1), 'glass')

class TntTrailArrow(metaclass=SpecialArrow):
    COLOR = 0xff0000

    def every_tick():
        Statement(f'summon tnt')


# langcraft debug output

out = compile_all(write=True, root_dir='../datapacks/special_arrows')
display_all()
