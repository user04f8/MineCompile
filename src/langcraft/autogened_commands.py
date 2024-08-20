
from __future__ import annotations
from typing import Optional, Literal, Union

from .commands import StructuredCommand

import langcraft
from .minecraft_builtins import _AttributeType, EffectType, EntityType, BlockType
from .base_types import ObjectiveCriteria, ObjectiveName
from .serialize import CommandKeywordToken, StrToken, IntToken, FloatToken, BoolToken, MiscToken
class mc:

    class Advancement:
        def __init__(self):
            raise UserWarning("Invalid use of grant")

        class grant(StructuredCommand):
            def __init__(self):
                raise UserWarning("Invalid use of everything")

            class __everything(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['grant', '$arg', 'everything']

            @classmethod
            def everything(cls, targets: langcraft.mutables.Entities, add=True):
                return cls.__everything()._finalize([MiscToken(targets)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of only")

            class __only(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['grant', '$arg', 'only', '$arg', '$arg']

            @classmethod
            def only(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, criterion: str, add=True):
                return cls.__only()._finalize([MiscToken(targets), MiscToken(advancement), StrToken(criterion)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of from")

            class __from_(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['grant', '$arg', 'from', '$arg']

            @classmethod
            def from_(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__from_()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of through")

            class __through(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['grant', '$arg', 'through', '$arg']

            @classmethod
            def through(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__through()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of until")

            class __until(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['grant', '$arg', 'until', '$arg']

            @classmethod
            def until(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__until()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

        def __init__(self):
            raise UserWarning("Invalid use of revoke")

        class revoke(StructuredCommand):
            def __init__(self):
                raise UserWarning("Invalid use of everything")

            class __everything(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['revoke', '$arg', 'everything']

            @classmethod
            def everything(cls, targets: langcraft.mutables.Entities, add=True):
                return cls.__everything()._finalize([MiscToken(targets)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of only")

            class __only(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['revoke', '$arg', 'only', '$arg', '$arg']

            @classmethod
            def only(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, criterion: str, add=True):
                return cls.__only()._finalize([MiscToken(targets), MiscToken(advancement), StrToken(criterion)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of from")

            class __from_(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['revoke', '$arg', 'from', '$arg']

            @classmethod
            def from_(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__from_()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of through")

            class __through(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['revoke', '$arg', 'through', '$arg']

            @classmethod
            def through(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__through()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of until")

            class __until(StructuredCommand):
                NAME = 'advancement'
                FORMAT = ['revoke', '$arg', 'until', '$arg']

            @classmethod
            def until(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__until()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)


    class Attribute:
        def __init__(self):
            raise UserWarning("Invalid use of get")

        class __get(StructuredCommand):
            NAME = 'attribute'
            FORMAT = [None, None, 'get', '$optional_arg']

        @classmethod
        def get(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, scale: Optional[float] = None, add=True):
            return cls.__get()._finalize([MiscToken(target), MiscToken(attribute), (None if scale is None else FloatToken(scale))], add=add)

        def __init__(self):
            raise UserWarning("Invalid use of set")

        class __set(StructuredCommand):
            NAME = 'attribute'
            FORMAT = [None, None, 'set', '$arg']

        @classmethod
        def set(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, value: float, add=True):
            return cls.__set()._finalize([MiscToken(target), MiscToken(attribute), FloatToken(value)], add=add)

        def __init__(self):
            raise UserWarning("Invalid use of modifier")

        class modifier(StructuredCommand):
            def __init__(self):
                raise UserWarning("Invalid use of add")

            class add(StructuredCommand):
                def __init__(self):
                    raise UserWarning("Invalid use of add_value")

                class __add_value(StructuredCommand):
                    NAME = 'attribute'
                    FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_value']

                @classmethod
                def add_value(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                    return cls.__add_value()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of add_multiplied_base")

                class __add_multiplied_base(StructuredCommand):
                    NAME = 'attribute'
                    FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_base']

                @classmethod
                def add_multiplied_base(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                    return cls.__add_multiplied_base()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of add_multiplied_total")

                class __add_multiplied_total(StructuredCommand):
                    NAME = 'attribute'
                    FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_total']

                @classmethod
                def add_multiplied_total(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                    return cls.__add_multiplied_total()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of remove")

            class __remove(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'remove', '$arg']

            @classmethod
            def remove(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__remove()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of value")

            class value(StructuredCommand):
                def __init__(self):
                    raise UserWarning("Invalid use of get")

                class __get(StructuredCommand):
                    NAME = 'attribute'
                    FORMAT = [None, None, 'modifier', 'value', 'get', '$arg']

                @classmethod
                def get(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, add=True):
                    return cls.__get()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id)], add=add)


    class Effect:
        def __init__(self):
            raise UserWarning("Invalid use of clear")

        class __clear(StructuredCommand):
            NAME = 'effect'
            FORMAT = ['clear', '$optional_arg', '$optional_arg']

        @classmethod
        def clear(cls, targets: Optional[langcraft.mutables.Entities] = None, effect: Optional[EffectType] = None, add=True):
            return cls.__clear()._finalize([(None if targets is None else MiscToken(targets)), (None if effect is None else MiscToken(effect))], add=add)

        def __init__(self):
            raise UserWarning("Invalid use of give")

        class __give(StructuredCommand):
            NAME = 'effect'
            FORMAT = ['give', '$arg', '$arg', '$optional_arg', '$optional_arg', '$optional_arg']

        @classmethod
        def give(cls, targets: langcraft.mutables.Entities, effect: EffectType, seconds: Optional[Union[int, Literal['infinite']]] = None, amplifier: Optional[int] = None, hide_particles: Optional[bool] = None, add=True):
            return cls.__give()._finalize([MiscToken(targets), MiscToken(effect), (None if seconds is None else (IntToken(seconds) if isinstance(seconds, Union[int, Literal['infinite']]) else CommandKeywordToken(seconds))), (None if amplifier is None else IntToken(amplifier)), (None if hide_particles is None else BoolToken(hide_particles))], add=add)


    class Scoreboard:
        def __init__(self):
            raise UserWarning("Invalid use of objectives")

        class objectives(StructuredCommand):
            def __init__(self):
                raise UserWarning("Invalid use of list")

            class __list(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'list']

            @classmethod
            def list(cls, add=True):
                return cls.__list()._finalize([], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of add")

            class __add(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'add', '$arg', '$arg', '$optional_arg']

            @classmethod
            def add(cls, objective: ObjectiveName, criteria: str, display_name: Optional[str] = None, add=True):
                return cls.__add()._finalize([MiscToken(objective), StrToken(criteria), (None if display_name is None else StrToken(display_name))], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of remove")

            class __remove(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'remove', '$arg']

            @classmethod
            def remove(cls, objective: ObjectiveName, add=True):
                return cls.__remove()._finalize([MiscToken(objective)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of <langcraft.autogen.mc_syntax.Alias object at 0x0000022BDEF62690>")

            class __set_display(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'setdisplay', '$arg', '$optional_arg']

            @classmethod
            def set_display(cls, slot: str, objective: Optional[str] = None, add=True):
                return cls.__set_display()._finalize([StrToken(slot), (None if objective is None else StrToken(objective))], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of modify")

            class modify(StructuredCommand):
                def __init__(self):
                    raise UserWarning("Invalid use of <langcraft.autogen.mc_syntax.Alias object at 0x0000022BDEF62720>")

                class __display_auto_update(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'displayautoupdate', '$arg']

                @classmethod
                def display_auto_update(cls, objective: ObjectiveName, value: bool, add=True):
                    return cls.__display_auto_update()._finalize([MiscToken(objective), BoolToken(value)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of <langcraft.autogen.mc_syntax.Alias object at 0x0000022BDEF62780>")

                class __display_name(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'displayname', '$arg']

                @classmethod
                def display_name(cls, objective: ObjectiveName, display_name: str, add=True):
                    return cls.__display_name()._finalize([MiscToken(objective), StrToken(display_name)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of <langcraft.autogen.mc_syntax.Alias object at 0x0000022BDEF627E0>")

                class number_format(StructuredCommand):
                    def __init__(self):
                        raise UserWarning("Invalid use of <langcraft.autogen.mc_syntax.Alias object at 0x0000022BDEF62810>")

                    class __reset(StructuredCommand):
                        NAME = 'scoreboard'
                        FORMAT = ['objectives', 'modify', '$arg', 'numberformat']

                    @classmethod
                    def reset(cls, objective: ObjectiveName, add=True):
                        return cls.__reset()._finalize([MiscToken(objective)], add=add)

                    def __init__(self):
                        raise UserWarning("Invalid use of blank")

                    class __blank(StructuredCommand):
                        NAME = 'scoreboard'
                        FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'blank']

                    @classmethod
                    def blank(cls, objective: ObjectiveName, add=True):
                        return cls.__blank()._finalize([MiscToken(objective)], add=add)

                    def __init__(self):
                        raise UserWarning("Invalid use of fixed")

                    class __fixed(StructuredCommand):
                        NAME = 'scoreboard'
                        FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'fixed', '$arg']

                    @classmethod
                    def fixed(cls, objective: ObjectiveName, component: str | langcraft.serialize_types.JSONText, add=True):
                        return cls.__fixed()._finalize([MiscToken(objective), (StrToken(component) if isinstance(component, str | langcraft.serialize_types.JSONText) else MiscToken(component))], add=add)

                    def __init__(self):
                        raise UserWarning("Invalid use of styled")

                    class __styled(StructuredCommand):
                        NAME = 'scoreboard'
                        FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'styled', '$arg']

                    @classmethod
                    def styled(cls, objective: ObjectiveName, style: langcraft.serialize_types.JSONText, add=True):
                        return cls.__styled()._finalize([MiscToken(objective), MiscToken(style)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of rendertype")

                class __rendertype(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'rendertype', '$arg']

                @classmethod
                def rendertype(cls, objective: ObjectiveName, rendertype: Literal['hearts', 'integer'], add=True):
                    return cls.__rendertype()._finalize([MiscToken(objective), CommandKeywordToken(rendertype)], add=add)

        def __init__(self):
            raise UserWarning("Invalid use of players")

        class players(StructuredCommand):
            def __init__(self):
                raise UserWarning("Invalid use of list")

            class __list(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'list', '$optional_arg']

            @classmethod
            def list(cls, target: Optional[langcraft.mutables.Entity] = None, add=True):
                return cls.__list()._finalize([(None if target is None else MiscToken(target))], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of get")

            class __get(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'get', '$arg', '$arg']

            @classmethod
            def get(cls, target: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                return cls.__get()._finalize([MiscToken(target), MiscToken(objective)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of set")

            class __set(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'set', '$arg', '$arg', '$arg']

            @classmethod
            def set(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
                return cls.__set()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of add")

            class __add(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'add', '$arg', '$arg', '$arg']

            @classmethod
            def add(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
                return cls.__add()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of remove")

            class __remove(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'remove', '$arg', '$arg', '$arg']

            @classmethod
            def remove(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
                return cls.__remove()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of reset")

            class __reset(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'reset', '$arg', '$optional_arg']

            @classmethod
            def reset(cls, targets: langcraft.mutables.Entities, objective: Optional[ObjectiveName] = None, add=True):
                return cls.__reset()._finalize([MiscToken(targets), (None if objective is None else MiscToken(objective))], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of enable")

            class __enable(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'enable', '$arg', '$arg']

            @classmethod
            def enable(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                return cls.__enable()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of operation")

            class __operation(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'operation', '$arg', '$arg', '$arg', '$arg', '$arg']

            @classmethod
            def operation(cls, targets: langcraft.mutables.Entities, target_objective: ObjectiveName, operation: Literal['=', '+=', '-=', '*=', '/=', '%=', '><', '<', '>'], source: langcraft.mutables.Entities, source_objective: ObjectiveName, add=True):
                return cls.__operation()._finalize([MiscToken(targets), MiscToken(target_objective), CommandKeywordToken(operation), MiscToken(source), MiscToken(source_objective)], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of display_name")

            class display_name(StructuredCommand):
                def __init__(self):
                    raise UserWarning("Invalid use of reset")

                class __reset(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_name', 'reset', '$arg', '$arg']

                @classmethod
                def reset(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                    return cls.__reset()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of set")

                class __set(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_name', 'set', '$arg', '$arg', '$arg']

                @classmethod
                def set(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, text: str | langcraft.serialize_types.JSONText, add=True):
                    return cls.__set()._finalize([MiscToken(targets), MiscToken(objective), (StrToken(text) if isinstance(text, str | langcraft.serialize_types.JSONText) else MiscToken(text))], add=add)

            def __init__(self):
                raise UserWarning("Invalid use of display_numberformat")

            class display_numberformat(StructuredCommand):
                def __init__(self):
                    raise UserWarning("Invalid use of reset")

                class __reset(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_numberformat', 'reset', '$arg', '$arg']

                @classmethod
                def reset(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                    return cls.__reset()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of blank")

                class __blank(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_numberformat', 'blank', '$arg', '$arg']

                @classmethod
                def blank(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                    return cls.__blank()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of fixed")

                class __fixed(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_numberformat', 'fixed', '$arg', '$arg', '$arg']

                @classmethod
                def fixed(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, contents: str | langcraft.serialize_types.JSONText, add=True):
                    return cls.__fixed()._finalize([MiscToken(targets), MiscToken(objective), (StrToken(contents) if isinstance(contents, str | langcraft.serialize_types.JSONText) else MiscToken(contents))], add=add)

                def __init__(self):
                    raise UserWarning("Invalid use of styled")

                class __styled(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['players', 'display_numberformat', 'styled', '$arg', '$arg', '$arg']

                @classmethod
                def styled(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, style: langcraft.serialize_types.JSONText, add=True):
                    return cls.__styled()._finalize([MiscToken(targets), MiscToken(objective), MiscToken(style)], add=add)

