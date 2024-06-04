from typing import List, Self

from .base import Statement
from .serialize import *
from .misc_types import *

class RawCommand(Statement):
    NAME: str

    def __init__(self, *tokens: Token, add=True):
        # if isinstance(tokens, str):
        #     tokens = [StrToken(token) for token in tokens.split()]
        super().__init__(self, Command(CommandToken(self.NAME), *tokens), add=add)

class Advancement(RawCommand):
    NAME = 'advancement'

    def __init__(self, *tokens: Token, add=True):
        super().__init__(*tokens, add=add)

    @classmethod
    def grant(cls, target):
        return cls(CommandSubToken('grant'), target, add=False)

    @classmethod
    def revoke(cls, target):
        return cls(CommandSubToken('revoke'), target, add=False)

    def everything(self):
        return Advancement(*self.tokens, CommandSubToken('everything'))

    def only(self, advancement, criterion=None):
        if criterion:
            return Advancement(*self.tokens, CommandSubToken('only'), advancement, criterion)
        return Advancement(*self.tokens, CommandSubToken('only'), advancement)

    def from_(self, advancement):
        return Advancement(*self.tokens, CommandSubToken('from'), advancement)

    def through(self, advancement):
        return Advancement(*self.tokens, CommandSubToken('through'), advancement)

    def until(self, advancement):
        return Advancement(*self.tokens, CommandSubToken('until'), advancement)

# Example usage:
selector = Selector()
adv = Advancement.grant(selector).everything()

# class Advancement(RawCommand):
#     NAME = 'advancement'

#     class Grant:
#         NAME = 'grant'
#         def __init__(self):
#             self.targets = Selector()

#         def __call__(self, targets: Selector):
#             self.targets = targets
#             return self
        
#         class Everything:
#             NAME = 'everything'
#             def __init__(self, parent):
#                 self.parent = parent

#             def __call__(self):
#                 return Advancement(CommandSubToken(self.parent.NAME), CommandSubToken(self.NAME))

#         class Sub1_Advancement:
#             def __init__(self, x):
#                 self.x1 = x
            
#             def __call__(self, advancement: ResourceLocation):
#                 self.advancement = advancement
#                 return Advancement(CommandSubToken(self.x), CommandSubToken())
        
#         class Sub1_AdvancementCriterion:
#             def __init__(self, x):
#                 self.x1 = x

#             def __call__(self, advancement: ResourceLocation, criterion: str = ''):
#                 self.advancement = advancement
#                 self.criterion = criterion
        
#         everything = Everything()
#         only = Sub1_AdvancementCriterion(Self, 'only')
#         from_ = Sub1_Advancement(Self, 'from')
#         through = Sub1_Advancement(Self, 'through')
#         until = Sub1_Advancement(Self, 'until')

#     grant = Grant()
#     revoke = Revoke()

# Advancement.grant(Selector()).everything()

