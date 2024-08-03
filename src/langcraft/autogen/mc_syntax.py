from typing import Literal

from langcraft.minecraft_builtins import EffectType, EntityType, BlockType, _AttributeType
from langcraft.base_types import ObjectiveName, ObjectiveCriteria
from langcraft.mutables import Entities, Entity, Players, Player
from langcraft.serialize_types import ResourceLocation, JSONText
Component = str | JSONText
ComponentStyle = JSONText  # TODO

MC_IMPORTS: dict[str, set[str]] = {
    '.minecraft_builtins': {EffectType, EntityType, BlockType, _AttributeType},
    '.base_types': {ObjectiveName, ObjectiveCriteria},
    # '.mutables': {Entities, SingleEntity, Players, SinglePlayer},  # note: classes don't need to be included
}

class Alias:
    def __init__(self, python_name, mc_name):
        self.mc_name = mc_name
        self.python_name = python_name

type CommandType = type | list[CommandType]

class Args:
    def __init__(self, **kwargs: CommandType):
        self.args: dict[str, CommandType] = kwargs
        self.next_command_def: dict | None = None

    def __add__(self, command_def):
        self.next_command_def = command_def
        return self

type CommandDef = dict[str, CommandDef | None | Args]

_advancement_sub = Args(targets=Entities) + {
    'everything': None,
    'only': Args(advancement=ResourceLocation, criterion=str),
    'from': Args(advancement=ResourceLocation),
    'through': Args(advancement=ResourceLocation),
    'until': Args(advancement=ResourceLocation)
}

COMMANDS: CommandDef = {
    'advancement': {
        'grant': _advancement_sub,
        'revoke': _advancement_sub
    },
    'attribute': Args(target=Entities, attribute=_AttributeType) + {
        'get': Args(scale=[float]),
        'set': Args(value=float),
        'modifier': {
            'add': Args(id=ResourceLocation, value=float) + {
                'add_value': None, 'add_multiplied_base': None, 'add_multiplied_total': None
            },
            'remove': Args(id=ResourceLocation),
            'value': {
                'get': Args(id=ResourceLocation)
            }
        }
    },
    'effect': {
        'clear': Args(targets=[Entities], effect=[EffectType]),
        'give': Args(targets=Entities, effect=EffectType, seconds=[int | Literal['infinite']], amplifier=[int], hideParticles=[bool])
    },
    'scoreboard': {
        'objectives': {
            'list': Args(),
            'add': Args(objective=ObjectiveName, criteria=str, displayName=[str]),
            'remove': Args(objective=ObjectiveName),
            Alias('set_display', 'setdisplay'): Args(slot=str, objective=[str]),
            'modify': Args(objective=ObjectiveName) + {
                Alias('display_auto_update', 'displayautoupdate'): Args(value=bool),
                Alias('display_name', 'displayname'): Args(displayName=str),
                Alias('number_format', 'numberformat'): {
                    Alias('reset', None): Args(),
                    'blank': Args(),
                    'fixed': Args(component=Component),
                    'styled': Args(style=ComponentStyle)
                },
                'rendertype': Args(rendertype=Literal['hearts', 'integer'])
            }
        },
        'players': {
            'list': Args(target=[Entity]),  # see MC-136858
            'get': Args(target=Entities, objective=ObjectiveName),
            'set': Args(targets=Entities, objective=ObjectiveName, score=int),
            'add': Args(targets=Entities, objective=ObjectiveName, score=int),
            'remove': Args(targets=Entities, objective=ObjectiveName, score=int),
            'reset': Args(targets=Entities, objective=[ObjectiveName]),
            'enable': Args(targets=Entities, objective=ObjectiveName),
            'operation': Args(targets=Entities, targetObjective=ObjectiveName, operation=Literal['=', '+=', '-=', '*=', '/=', '%=', '><', '<', '>'], source=Entities, sourceObjective=ObjectiveName),
            'display_name': {
                'reset': Args(targets=Entities, objective=ObjectiveName),
                'set': Args(targets=Entities, objective=ObjectiveName, text=Component)
            },
            'display_numberformat': {
                'reset': Args(targets=Entities, objective=ObjectiveName),
                'blank': Args(targets=Entities, objective=ObjectiveName),
                'fixed': Args(targets=Entities, objective=ObjectiveName, contents=Component),
                'styled': Args(targets=Entities, objective=ObjectiveName, style=ComponentStyle)
            }
        }
    }
}