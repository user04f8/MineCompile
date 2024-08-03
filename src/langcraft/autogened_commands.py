
from __future__ import annotations
from typing import Optional, Literal, Union

from .commands import StructuredCommand


import langcraft
from .minecraft_builtins import EntityType, _AttributeType, BlockType, EffectType
from .base_types import ObjectiveName, ObjectiveCriteria
from .serialize import IntToken, CommandKeywordToken, StrToken, FloatToken, MiscToken, BoolToken
__all__ = ('Advancement', 'Attribute', 'Effect', 'Scoreboard')

class Advancement:
    class grant(StructuredCommand):
        class __everything(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'everything']

        @classmethod
        def everything(cls, targets: langcraft.mutables.Entities, add=True):
            return cls.__everything()._finalize([MiscToken(targets)], add=add)

        class __only(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'only', '$arg', '$arg']

        @classmethod
        def only(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, criterion: str, add=True):
            return cls.__only()._finalize([MiscToken(targets), MiscToken(advancement), StrToken(criterion)], add=add)

        class __from_(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'from', '$arg']

        @classmethod
        def from_(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__from_()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

        class __through(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'through', '$arg']

        @classmethod
        def through(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__through()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

        class __until(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'until', '$arg']

        @classmethod
        def until(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__until()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

    class revoke(StructuredCommand):
        class __everything(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'everything']

        @classmethod
        def everything(cls, targets: langcraft.mutables.Entities, add=True):
            return cls.__everything()._finalize([MiscToken(targets)], add=add)

        class __only(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'only', '$arg', '$arg']

        @classmethod
        def only(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, criterion: str, add=True):
            return cls.__only()._finalize([MiscToken(targets), MiscToken(advancement), StrToken(criterion)], add=add)

        class __from_(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'from', '$arg']

        @classmethod
        def from_(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__from_()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

        class __through(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'through', '$arg']

        @classmethod
        def through(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__through()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)

        class __until(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'until', '$arg']

        @classmethod
        def until(cls, targets: langcraft.mutables.Entities, advancement: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__until()._finalize([MiscToken(targets), MiscToken(advancement)], add=add)


class Attribute:
    class __get(StructuredCommand):
        NAME = 'attribute'
        FORMAT = [None, None, 'get', '$optional_arg']

    @classmethod
    def get(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, scale: Optional[float] = None, add=True):
        return cls.__get()._finalize([MiscToken(target), MiscToken(attribute), (None if scale is None else FloatToken(scale))], add=add)

    class __set(StructuredCommand):
        NAME = 'attribute'
        FORMAT = [None, None, 'set', '$arg']

    @classmethod
    def set(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, value: float, add=True):
        return cls.__set()._finalize([MiscToken(target), MiscToken(attribute), FloatToken(value)], add=add)

    class modifier(StructuredCommand):
        class add(StructuredCommand):
            class __add_value(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_value']

            @classmethod
            def add_value(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                return cls.__add_value()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

            class __add_multiplied_base(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_base']

            @classmethod
            def add_multiplied_base(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                return cls.__add_multiplied_base()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

            class __add_multiplied_total(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_total']

            @classmethod
            def add_multiplied_total(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, value: float, add=True):
                return cls.__add_multiplied_total()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id), FloatToken(value)], add=add)

        class __remove(StructuredCommand):
            NAME = 'attribute'
            FORMAT = [None, None, 'modifier', 'remove', '$arg']

        @classmethod
        def remove(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, add=True):
            return cls.__remove()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id)], add=add)

        class value(StructuredCommand):
            class __get(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'value', 'get', '$arg']

            @classmethod
            def get(cls, target: langcraft.mutables.Entities, attribute: _AttributeType, id: langcraft.serialize_types.ResourceLocation, add=True):
                return cls.__get()._finalize([MiscToken(target), MiscToken(attribute), MiscToken(id)], add=add)


class Effect:
    class __clear(StructuredCommand):
        NAME = 'effect'
        FORMAT = ['clear', '$optional_arg', '$optional_arg']

    @classmethod
    def clear(cls, targets: Optional[langcraft.mutables.Entities] = None, effect: Optional[EffectType] = None, add=True):
        return cls.__clear()._finalize([(None if targets is None else MiscToken(targets)), (None if effect is None else MiscToken(effect))], add=add)

    class __give(StructuredCommand):
        NAME = 'effect'
        FORMAT = ['give', '$arg', '$arg', '$optional_arg', '$optional_arg', '$optional_arg']

    @classmethod
    def give(cls, targets: langcraft.mutables.Entities, effect: EffectType, seconds: Optional[Union[int, Literal['infinite']]] = None, amplifier: Optional[int] = None, hide_particles: Optional[bool] = None, add=True):
        return cls.__give()._finalize([MiscToken(targets), MiscToken(effect), (None if seconds is None else (IntToken(seconds) if isinstance(seconds, Union[int, Literal['infinite']]) else CommandKeywordToken(seconds))), (None if amplifier is None else IntToken(amplifier)), (None if hide_particles is None else BoolToken(hide_particles))], add=add)


class Scoreboard:
    class objectives(StructuredCommand):
        class __list(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'list']

        @classmethod
        def list(cls, add=True):
            return cls.__list()._finalize([], add=add)

        class __add(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'add', '$arg', '$arg', '$optional_arg']

        @classmethod
        def add(cls, objective: ObjectiveName, criteria: str, display_name: Optional[str] = None, add=True):
            return cls.__add()._finalize([MiscToken(objective), StrToken(criteria), (None if display_name is None else StrToken(display_name))], add=add)

        class __remove(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'remove', '$arg']

        @classmethod
        def remove(cls, objective: ObjectiveName, add=True):
            return cls.__remove()._finalize([MiscToken(objective)], add=add)

        class __set_display(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'setdisplay', '$arg', '$optional_arg']

        @classmethod
        def set_display(cls, slot: str, objective: Optional[str] = None, add=True):
            return cls.__set_display()._finalize([StrToken(slot), (None if objective is None else StrToken(objective))], add=add)

        class modify(StructuredCommand):
            class __display_auto_update(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'displayautoupdate', '$arg']

            @classmethod
            def display_auto_update(cls, objective: ObjectiveName, value: bool, add=True):
                return cls.__display_auto_update()._finalize([MiscToken(objective), BoolToken(value)], add=add)

            class __display_name(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'displayname', '$arg']

            @classmethod
            def display_name(cls, objective: ObjectiveName, display_name: str, add=True):
                return cls.__display_name()._finalize([MiscToken(objective), StrToken(display_name)], add=add)

            class number_format(StructuredCommand):
                class __reset(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat']

                @classmethod
                def reset(cls, objective: ObjectiveName, add=True):
                    return cls.__reset()._finalize([MiscToken(objective)], add=add)

                class __blank(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'blank']

                @classmethod
                def blank(cls, objective: ObjectiveName, add=True):
                    return cls.__blank()._finalize([MiscToken(objective)], add=add)

                class __fixed(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'fixed', '$arg']

                @classmethod
                def fixed(cls, objective: ObjectiveName, component: str | langcraft.serialize_types.JSONText, add=True):
                    return cls.__fixed()._finalize([MiscToken(objective), (StrToken(component) if isinstance(component, str | langcraft.serialize_types.JSONText) else MiscToken(component))], add=add)

                class __styled(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'styled', '$arg']

                @classmethod
                def styled(cls, objective: ObjectiveName, style: langcraft.serialize_types.JSONText, add=True):
                    return cls.__styled()._finalize([MiscToken(objective), MiscToken(style)], add=add)

            class __rendertype(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'rendertype', '$arg']

            @classmethod
            def rendertype(cls, objective: ObjectiveName, rendertype: Literal['hearts', 'integer'], add=True):
                return cls.__rendertype()._finalize([MiscToken(objective), CommandKeywordToken(rendertype)], add=add)

    class players(StructuredCommand):
        class __list(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'list', '$optional_arg']

        @classmethod
        def list(cls, target: Optional[langcraft.mutables.Entity] = None, add=True):
            return cls.__list()._finalize([(None if target is None else MiscToken(target))], add=add)

        class __get(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'get', '$arg', '$arg']

        @classmethod
        def get(cls, target: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
            return cls.__get()._finalize([MiscToken(target), MiscToken(objective)], add=add)

        class __set(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'set', '$arg', '$arg', '$arg']

        @classmethod
        def set(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
            return cls.__set()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

        class __add(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'add', '$arg', '$arg', '$arg']

        @classmethod
        def add(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
            return cls.__add()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

        class __remove(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'remove', '$arg', '$arg', '$arg']

        @classmethod
        def remove(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, score: int, add=True):
            return cls.__remove()._finalize([MiscToken(targets), MiscToken(objective), IntToken(score)], add=add)

        class __reset(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'reset', '$arg', '$optional_arg']

        @classmethod
        def reset(cls, targets: langcraft.mutables.Entities, objective: Optional[ObjectiveName] = None, add=True):
            return cls.__reset()._finalize([MiscToken(targets), (None if objective is None else MiscToken(objective))], add=add)

        class __enable(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'enable', '$arg', '$arg']

        @classmethod
        def enable(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
            return cls.__enable()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

        class __operation(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['players', 'operation', '$arg', '$arg', '$arg', '$arg', '$arg']

        @classmethod
        def operation(cls, targets: langcraft.mutables.Entities, target_objective: ObjectiveName, operation: Literal['=', '+=', '-=', '*=', '/=', '%=', '><', '<', '>'], source: langcraft.mutables.Entities, source_objective: ObjectiveName, add=True):
            return cls.__operation()._finalize([MiscToken(targets), MiscToken(target_objective), CommandKeywordToken(operation), MiscToken(source), MiscToken(source_objective)], add=add)

        class display_name(StructuredCommand):
            class __reset(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_name', 'reset', '$arg', '$arg']

            @classmethod
            def reset(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                return cls.__reset()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

            class __set(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_name', 'set', '$arg', '$arg', '$arg']

            @classmethod
            def set(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, text: str | langcraft.serialize_types.JSONText, add=True):
                return cls.__set()._finalize([MiscToken(targets), MiscToken(objective), (StrToken(text) if isinstance(text, str | langcraft.serialize_types.JSONText) else MiscToken(text))], add=add)

        class display_numberformat(StructuredCommand):
            class __reset(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_numberformat', 'reset', '$arg', '$arg']

            @classmethod
            def reset(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                return cls.__reset()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

            class __blank(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_numberformat', 'blank', '$arg', '$arg']

            @classmethod
            def blank(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, add=True):
                return cls.__blank()._finalize([MiscToken(targets), MiscToken(objective)], add=add)

            class __fixed(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_numberformat', 'fixed', '$arg', '$arg', '$arg']

            @classmethod
            def fixed(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, contents: str | langcraft.serialize_types.JSONText, add=True):
                return cls.__fixed()._finalize([MiscToken(targets), MiscToken(objective), (StrToken(contents) if isinstance(contents, str | langcraft.serialize_types.JSONText) else MiscToken(contents))], add=add)

            class __styled(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['players', 'display_numberformat', 'styled', '$arg', '$arg', '$arg']

            @classmethod
            def styled(cls, targets: langcraft.mutables.Entities, objective: ObjectiveName, style: langcraft.serialize_types.JSONText, add=True):
                return cls.__styled()._finalize([MiscToken(targets), MiscToken(objective), MiscToken(style)], add=add)

