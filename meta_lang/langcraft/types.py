from termcolor import colored

from .serialize import Token, RawToken, SelectorToken, Serializable

class Int32(Token):
    MIN = -2**31
    MAX = 2**31 - 1
    def __init__(self, x: int):
        assert self.MIN <= x <= self.MAX
        self.x = x

    def __str__(self):
        return str(self.x)


class ResourceLocation(Serializable):
    def __init__(self, s = 's', **kwargs):
        self.token: RawToken = RawToken(s, **kwargs)

class Selector(Serializable):
    def __init__(self, s = 's', **kwargs):
        self.token: SelectorToken = SelectorToken(s, **kwargs)

    def as_(self):
        return [self.token] # TODO

class SingleSelector(Selector):
    def __init__(self, s: str | Selector = 's', **kwargs) -> None:
        if isinstance(s, Selector):
            self.token = s.token
        else:
            super().__init__(s, **kwargs)
        if self.token.s not in {'p', 'r', 's', 'n'}:
            if 'limit' in self.token.kwargs and self.token.kwargs['limit'] != 1:
                raise ValueError(f"Non-singular selector token with limit={self.token.kwargs['limit']}")
            self.token.kwargs['limit'] = 1

class EntitySelector(Selector):
    def __init__(self, **kwargs):
        return Selector('e', **kwargs)
    
class VarToken(Token):
    def __init__(self, entity_ref: Selector, name: str):
        self.entity_ref = SingleSelector(entity_ref)
        self.name = name

    def __str__(self):
        return f'{self.entity_ref} {self.name}'
