from typing import Optional, Literal, Self

from .serialize import StrToken
from .commands import StructuredCommand

class classproperty:
    def __init__(self, func):
        self.fget = func
    def __get__(self, instance, owner):
        return self.fget(owner)

class Scoreboard(StructuredCommand):
    NAME = 'scoreboard'

    # @classmethod
    # def objectives(cls):
    #     return cls('objectives')

    def list(self):
        self._add_kw('list')
        self._finalize()
        return self

    def add(self, objective: str, criteria: str, display_name: Optional[str] = None):
        self._add_kw('add')
        self._add_token(StrToken(objective))
        self._add_token(StrToken(criteria))
        if display_name is not None:
            self._add_token(StrToken(display_name))
        self._finalize()
        return self

    def remove(self, objective: str):
        self._add_kw('remove')
        self._add_token(StrToken(objective))
        self._finalize()
        return self

    def set_display(self, slot: str, objective: Optional[str] = None):
        self._add_kw('setdisplay')
        self._add_token(StrToken(slot))
        if objective is not None:
            self._add_token(StrToken(objective))
        self._finalize()
        return self

    @property
    def modify(self):
        self._add_kw('modify')
        return self

    def display_auto_update(self, objective: str, value: str):
        self._add_kw('displayautoupdate')
        self._add_token(StrToken(objective))
        self._add_token(StrToken(value))
        self._finalize()
        return self

    def display_name(self, objective: str, display_name: str):
        self._add_kw('displayname')
        self._add_token(StrToken(objective))
        self._add_token(StrToken(display_name))
        self._finalize()
        return self

    @property
    def number_format(self):
        self._add_kw('numberformat')
        return self

    def reset(self, objective: str):
        self._add_token(StrToken(objective))
        self._finalize()
        return self

    def blank(self, objective: str):
        self._add_kw('blank')
        self._add_token(StrToken(objective))
        self._finalize()
        return self

    def fixed(self, objective: str, component: str):
        self._add_kw('fixed')
        self._add_token(StrToken(objective))
        self._add_token(StrToken(component))
        self._finalize()
        return self

    def styled(self, objective: str, style: str):
        self._add_kw('styled')
        self._add_token(StrToken(objective))
        self._add_token(StrToken(style))
        self._finalize()
        return self

    def rendertype(self, objective: str, rendertype: Literal['hearts', 'integer']):
        self._add_kw('rendertype')
        self._add_token(StrToken(objective))
        self._add_kw(rendertype)
        self._finalize()
        return self

Scoreboard.objectives.