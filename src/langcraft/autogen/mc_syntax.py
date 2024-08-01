import re
from typing import Literal

from langcraft.minecraft_builtins import EffectType, EntityType, BlockType, _AttributeType

def camel_to_snake(camel_str):
    # Replace all capital letters with underscore followed by the lowercase version of the letter
    snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    return snake_str

class Alias:
    def __init__(self, python_name, mc_name):
        self.mc_name = mc_name
        self.python_name = python_name

type CommandType = type | Literal['ResourceLocation', 'Entities', 'SingleEntity', 'Players', 'SinglePlayer'] | list[CommandType]

class Args:
    def __init__(self, **kwargs: CommandType):
        self.args: dict[str, CommandType] = kwargs
        self.next_command_def: dict | None = None

    def __add__(self, command_def):
        self.next_command_def = command_def
        return self

    def arg_strs(self) -> list[tuple[str, str, str]]:
        def arg_str(arg_type):
            if isinstance(arg_type, list):
                return 'Optional[' + arg_str(arg_type[0]) + '] = None'
            elif isinstance(arg_type, str):
                return arg_type
            elif arg_type is int:
                return 'int'
            elif arg_type is float:
                return 'float'
            elif arg_type is bool:
                return 'bool'
            elif arg_type is str:
                return 'str'
            else:
                return str(arg_type)
                # return arg_type.__name__

        return [(camel_to_snake(arg_name), arg_str(arg_type), arg_type) for arg_name, arg_type in self.args.items()]

type CommandDef = dict[str, CommandDef | None | Args]

_advancement_sub = Args(targets='Entities') + {
    'everything': None,
    'only': Args(advancement='ResourceLocation', criterion=str),
    'from': Args(advancement='ResourceLocation'),
    'through': Args(advancement='ResourceLocation'),
    'until': Args(advancement='ResourceLocation')
}

COMMANDS: CommandDef = {
    'advancement': {
        'grant': _advancement_sub,
        'revoke': _advancement_sub
    },
    'attribute': Args(target='Entities', attribute=_AttributeType) + {
        'get': Args(scale=[float]),
        'set': Args(value=float),
        'modifier': {
            'add': Args(id='ResourceLocation', value=float) + {
                'add_value': None, 'add_multiplied_base': None, 'add_multiplied_total': None
            },
            'remove': Args(id='ResourceLocation'),
            'value': {
                'get': Args(id='ResourceLocation')
            }
        }
    },
    'effect': {
        'clear': Args(targets=['Entities'], effect=[EffectType]),
        'give': Args(targets='Entities', effect=EffectType, seconds=[int | Literal['infinite']], amplifier=[int], hideParticles=[bool])
    },
    'scoreboard': {
        'objectives': {
            'list': Args(),
            'add': Args(objective=str, criteria=str, displayName=[str]),
            'remove': Args(objective=str),
            Alias('set_display', 'setdisplay'): Args(slot=str, objective=[str]),
            'modify': Args(objective=str) + {
                Alias('display_auto_update', 'displayautoupdate'): Args(value=bool),
                Alias('display_name', 'displayname'): Args(displayName=str),
                Alias('number_format', 'numberformat'): {
                    Alias('reset', None): Args(),
                    'blank': Args(),
                    'fixed': Args(component=str),
                    'styled': Args(style=str)
                },
                'rendertype': Args(rendertype=Literal['hearts', 'integer'])
            }
        }
    }
}