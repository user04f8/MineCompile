from typing import Optional, Literal

from .serialize import StrToken, BoolToken, CommandKeywordToken
from .commands import StructuredCommand
from .mutables import Entities

__all__ = ('Scoreboard', 'Effect')

class Scoreboard:
    class objectives(StructuredCommand):
        class __list(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'list']

        @classmethod
        def list(cls):
            return cls.__list()._finalize([])

        class __add(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'add', '$arg', '$arg', '$arg']

        @classmethod
        def add(cls, objective: str, criteria: str, display_name: Optional[str] = None):
            return cls.__add()._finalize([StrToken(objective), StrToken(criteria), (None if display_name is None else StrToken(display_name))])

        class __remove(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'remove', '$arg']

        @classmethod
        def remove(cls, objective: str):
            return cls.__remove()._finalize([StrToken(objective)])

        class __set_display(StructuredCommand):
            NAME = 'scoreboard'
            FORMAT = ['objectives', 'setdisplay', '$arg', '$arg']

        @classmethod
        def set_display(cls, slot: str, objective: Optional[str] = None):
            return cls.__set_display()._finalize([StrToken(slot), (None if objective is None else StrToken(objective))])

        class modify(StructuredCommand):
            class __display_auto_update(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'displayautoupdate', '$arg']

            @classmethod
            def display_auto_update(cls, objective: str, value: bool):
                return cls.__display_auto_update()._finalize([StrToken(objective), BoolToken(value)])

            class __display_name(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'displayname', '$arg']

            @classmethod
            def display_name(cls, objective: str, display_name: str):
                return cls.__display_name()._finalize([StrToken(objective), StrToken(display_name)])

            class number_format(StructuredCommand):
                class __reset(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat']

                @classmethod
                def reset(cls, objective: str):
                    return cls.__reset()._finalize([StrToken(objective)])

                class __blank(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'blank']

                @classmethod
                def blank(cls, objective: str):
                    return cls.__blank()._finalize([StrToken(objective)])

                class __fixed(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'fixed', '$arg']

                @classmethod
                def fixed(cls, objective: str, component: str):
                    return cls.__fixed()._finalize([StrToken(objective), StrToken(component)])

                class __styled(StructuredCommand):
                    NAME = 'scoreboard'
                    FORMAT = ['objectives', 'modify', '$arg', 'numberformat', 'styled', '$arg']

                @classmethod
                def styled(cls, objective: str, style: str):
                    return cls.__styled()._finalize([StrToken(objective), StrToken(style)])

            class __rendertype(StructuredCommand):
                NAME = 'scoreboard'
                FORMAT = ['objectives', 'modify', '$arg', 'rendertype', '$arg']

            @classmethod
            def rendertype(cls, objective: str, rendertype: Literal['hearts', 'integer']):
                return cls.__rendertype()._finalize([StrToken(objective), CommandKeywordToken(rendertype)])


class Effect:
    class __clear(StructuredCommand):
        NAME = 'effect'
        FORMAT = ['clear', '$arg', '$arg']

    @classmethod
    def clear(cls, targets: Optional[str] = None, effect: Optional[str] = None):
        return cls.__clear()._finalize([(None if targets is None else StrToken(targets)), (None if effect is None else StrToken(effect))])

    class give(StructuredCommand):
        def __call__(self, targets: Entities, effect: str, seconds: Optional[int] = None, amplifier: Optional[int] = None, hide_particles: Optional[bool] = None):
            self._finalize([targets, effect, seconds, amplifier, hide_particles])

        class __infinite(StructuredCommand):
            NAME = 'effect'
            FORMAT = ['give', '$arg', '$arg', 'infinite', '$arg', '$arg']

        @classmethod
        def infinite(cls, targets: Entities, effect: str, amplifier: Optional[int] = None, hide_particles: Optional[bool] = None):
            return cls.__infinite()._finalize([targets, StrToken(effect), (None if amplifier is None else amplifier), (None if hide_particles is None else BoolToken(hide_particles))])

Effect.give()