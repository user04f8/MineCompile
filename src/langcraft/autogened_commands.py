
from typing import Optional, Literal, Union

from .serialize import StrToken, BoolToken, IntToken, FloatToken, MiscToken, CommandKeywordToken
from .serialize_types import ResourceLocation
from .commands import StructuredCommand
from .mutables import Entities, SingleEntity, Players, SinglePlayer
from .minecraft_builtins import EffectType, EntityType, BlockType, _AttributeType

def resource_location_cast(x: str | ResourceLocation) -> ResourceLocation:
    if isinstance(x, str):
        return ResourceLocation('minecraft', x)
    return x

__all__ = ('Advancement', 'Attribute', 'Effect', 'Scoreboard')

class Advancement:
    class grant(StructuredCommand):
        class __everything(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'everything']

        @classmethod
        def everything(cls, targets: Entities, add=True):
            return cls.__everything()._finalize([targets], add=add)

        class __only(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'only', '$arg', '$arg']

        @classmethod
        def only(cls, targets: Entities, advancement: ResourceLocation, criterion: str, add=True):
            return cls.__only()._finalize([targets, resource_location_cast(advancement), StrToken(criterion)], add=add)

        class __from_(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'from', '$arg']

        @classmethod
        def from_(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__from_()._finalize([targets, resource_location_cast(advancement)], add=add)

        class __through(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'through', '$arg']

        @classmethod
        def through(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__through()._finalize([targets, resource_location_cast(advancement)], add=add)

        class __until(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['grant', '$arg', 'until', '$arg']

        @classmethod
        def until(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__until()._finalize([targets, resource_location_cast(advancement)], add=add)

    class revoke(StructuredCommand):
        class __everything(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'everything']

        @classmethod
        def everything(cls, targets: Entities, add=True):
            return cls.__everything()._finalize([targets], add=add)

        class __only(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'only', '$arg', '$arg']

        @classmethod
        def only(cls, targets: Entities, advancement: ResourceLocation, criterion: str, add=True):
            return cls.__only()._finalize([targets, resource_location_cast(advancement), StrToken(criterion)], add=add)

        class __from_(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'from', '$arg']

        @classmethod
        def from_(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__from_()._finalize([targets, resource_location_cast(advancement)], add=add)

        class __through(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'through', '$arg']

        @classmethod
        def through(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__through()._finalize([targets, resource_location_cast(advancement)], add=add)

        class __until(StructuredCommand):
            NAME = 'advancement'
            FORMAT = ['revoke', '$arg', 'until', '$arg']

        @classmethod
        def until(cls, targets: Entities, advancement: ResourceLocation, add=True):
            return cls.__until()._finalize([targets, resource_location_cast(advancement)], add=add)


class Attribute:
    class __get(StructuredCommand):
        NAME = 'attribute'
        FORMAT = [None, None, 'get', '$optional_arg']

    @classmethod
    def get(cls, target: Entities, attribute: _AttributeType, scale: Optional[float] = None, add=True):
        return cls.__get()._finalize([target, MiscToken(attribute), (None if scale is None else FloatToken(scale))], add=add)

    class __set(StructuredCommand):
        NAME = 'attribute'
        FORMAT = [None, None, 'set', '$arg']

    @classmethod
    def set(cls, target: Entities, attribute: _AttributeType, value: float, add=True):
        return cls.__set()._finalize([target, MiscToken(attribute), FloatToken(value)], add=add)

    class modifier(StructuredCommand):
        class add(StructuredCommand):
            class __add_value(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_value']

            @classmethod
            def add_value(cls, target: Entities, attribute: _AttributeType, id: ResourceLocation, value: float, add=True):
                return cls.__add_value()._finalize([target, MiscToken(attribute), resource_location_cast(id), FloatToken(value)], add=add)

            class __add_multiplied_base(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_base']

            @classmethod
            def add_multiplied_base(cls, target: Entities, attribute: _AttributeType, id: ResourceLocation, value: float, add=True):
                return cls.__add_multiplied_base()._finalize([target, MiscToken(attribute), resource_location_cast(id), FloatToken(value)], add=add)

            class __add_multiplied_total(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'add', '$arg', '$arg', 'add_multiplied_total']

            @classmethod
            def add_multiplied_total(cls, target: Entities, attribute: _AttributeType, id: ResourceLocation, value: float, add=True):
                return cls.__add_multiplied_total()._finalize([target, MiscToken(attribute), resource_location_cast(id), FloatToken(value)], add=add)

        class __remove(StructuredCommand):
            NAME = 'attribute'
            FORMAT = [None, None, 'modifier', 'remove', '$arg']

        @classmethod
        def remove(cls, target: Entities, attribute: _AttributeType, id: ResourceLocation, add=True):
            return cls.__remove()._finalize([target, MiscToken(attribute), resource_location_cast(id)], add=add)

        class value(StructuredCommand):
            class __get(StructuredCommand):
                NAME = 'attribute'
                FORMAT = [None, None, 'modifier', 'value', 'get', '$arg']

            @classmethod
            def get(cls, target: Entities, attribute: _AttributeType, id: ResourceLocation, add=True):
                return cls.__get()._finalize([target, MiscToken(attribute), resource_location_cast(id)], add=add)


class Effect:
    class __clear(StructuredCommand):
        NAME = 'effect'
        FORMAT = ['clear', '$optional_arg', '$optional_arg']

    @classmethod
    def clear(cls, targets: Optional[Entities] = None, effect: Optional[EffectType] = None, add=True):
        return cls.__clear()._finalize([(None if targets is None else targets), (None if effect is None else MiscToken(effect))], add=add)

    class __give(StructuredCommand):
        NAME = 'effect'
        FORMAT = ['give', '$arg', '$arg', '$optional_arg', '$optional_arg', '$optional_arg']

    @classmethod
    def give(cls, targets: Entities, effect: EffectType, seconds: Optional[Union[int, Literal['infinite']]] = None, amplifier: Optional[int] = None, hide_particles: Optional[bool] = None, add=True):
        return cls.__give()._finalize([targets, MiscToken(effect), (None if seconds is None else MiscToken(seconds)), (None if amplifier is None else IntToken(amplifier)), (None if hide_particles is None else BoolToken(hide_particles))], add=add)


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
        def add(cls, objective: str, criteria: str, display_name: Optional[str] = None, add=True):
            return cls.__add()._finalize([StrToken(objective), StrToken(criteria), (None if display_name is None else StrToken(display_name))], add=add)

        class __remove(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'remove', '$arg']

        @classmethod
        def remove(cls, objective: str, add=True):
            return cls.__remove()._finalize([StrToken(objective)], add=add)

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
            def display_auto_update(cls, objective: str, value: bool, add=True):
                return cls.__display_auto_update()._finalize([StrToken(objective), BoolToken(value)], add=add)

            class __display_name(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'displayname', '$arg']

            @classmethod
            def display_name(cls, objective: str, display_name: str, add=True):
                return cls.__display_name()._finalize([StrToken(objective), StrToken(display_name)], add=add)

            class number_format(StructuredCommand):
                class __reset(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat']

                @classmethod
                def reset(cls, objective: str, add=True):
                    return cls.__reset()._finalize([StrToken(objective)], add=add)

                class __blank(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'blank']

                @classmethod
                def blank(cls, objective: str, add=True):
                    return cls.__blank()._finalize([StrToken(objective)], add=add)

                class __fixed(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'fixed', '$arg']

                @classmethod
                def fixed(cls, objective: str, component: str, add=True):
                    return cls.__fixed()._finalize([StrToken(objective), StrToken(component)], add=add)

                class __styled(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'styled', '$arg']

                @classmethod
                def styled(cls, objective: str, style: str, add=True):
                    return cls.__styled()._finalize([StrToken(objective), StrToken(style)], add=add)

            class __rendertype(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'rendertype', '$arg']

            @classmethod
            def rendertype(cls, objective: str, rendertype: Literal['hearts', 'integer'], add=True):
                return cls.__rendertype()._finalize([StrToken(objective), CommandKeywordToken(rendertype)], add=add)

