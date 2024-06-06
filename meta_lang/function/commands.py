from enum import Enum
from typing import List, Self, Literal, Iterable

from .base import Statement, Fun
from .serialize import *
from .types import *

class ConditionType(Enum):
    FALSE = 0
    TRUE = 1
    STR = 3
    ALL = 10
    ANY = 11

class Condition:
    SIMPLE = {ConditionType.STR, }

    def __init__(self, value: str | List[Self] = '', condition_type: ConditionType = ConditionType.STR):
        self.condition_type = condition_type
        self.value = value
        self.inverted = False

    @property
    def always_true(self):
        return self.condition_type == ConditionType.TRUE
    
    @property
    def always_false(self):
        return self.condition_type == ConditionType.FALSE
    
    def __invert__(self) -> Self:
        if self.always_true:
            self.condition_type = ConditionType.FALSE
        elif self.always_false:
            self.condition_type = ConditionType.TRUE
        elif self.condition_type in {ConditionType.ANY, ConditionType.ALL}:
            self.value = [~sub_condition for sub_condition in self.value]  # De Morgan's laws
        else:
            self.inverted = not self.inverted

    def __and__(self, c: 'Condition') -> 'Condition':
        if self.always_false or c.always_true:
            return self
        elif self.always_true or c.always_false:
            return c
        elif self.condition_type == ConditionType.ALL:
            self.value: List[Condition]
            if c.condition_type == ConditionType.ALL:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        else:
            return Condition(condition_type=ConditionType.ALL, value=[self, c])

    def __or__(self, c: 'Condition') -> 'Condition':
        if self.always_false or c.always_true:
            return c
        elif self.always_true or c.always_false:
            return self
        if self.condition_type == ConditionType.ANY:
            if c.condition_type == ConditionType.ANY:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        return Condition(condition_type=ConditionType.ANY, value=[self, c])

    def tokenize(self) -> List[Token]:
        match self.condition_type:
            case ConditionType.STR:
                return [(CommandKeywordToken('unless') if self.inverted else CommandKeywordToken('if')), StrToken(self.value)]
            case ConditionType.ALL:
                if all(condition.condition_type in self.SIMPLE for condition in self.value):
                    return [token for condition in self.value for token in condition.tokenize()]
                else:
                    tokens = []
                    for i, condition in enumerate(self.value):
                        if condition.condition_type not in self.SIMPLE:
                            break
                        tokens += condition.tokenize()
                    rem_conditions = self.value[i:]
                    tokens += Fun.wrap_tokens([CommandNameToken('execute')] + [token for condition in rem_conditions for token in condition.tokenize()])
                    return tokens
            case ConditionType.ANY:
                self.value: List[Condition]
                return [ChoiceSpecialToken(*(c.tokenize() for c in self.value))]

class RawCommand(Statement):
    NAME: str

    def __init__(self, *tokens: Token, add=True):
        cmds = [self.as_cmd(*tokens)]
        # if isinstance(tokens, str):
        #     tokens = [StrToken(token) for token in tokens.split()]
        super().__init__(cmds, add=add)

    @classmethod
    def as_cmd(cls, *args, **kwargs) -> TokensContainer:
        # cmds = cls(*args, add=False).get_cmds()
        # assert len(cmds) == 0
        # return cmds[0]
        return TokensContainer(CommandNameToken(cls.NAME), *cls._gen_tokens(*args, **kwargs))
    
    @staticmethod
    def _gen_tokens(*args) -> Iterable[Token]:
        return args

class ExecuteSub:
    def __init__(self, subcmd: str, *args: Token):
        self.subcmd = CommandKeywordToken(subcmd)
        self.args = args

    def tokenize(self) -> List[Token]:
        return [self.subcmd, *self.args]

    @classmethod
    def align(cls):
        raise NotImplementedError

    @classmethod
    def anchored(cls):
        raise NotImplementedError

    @classmethod
    def as_(cls):
        raise NotImplementedError

    @classmethod
    def at(cls):
        raise NotImplementedError

    @classmethod
    def facing(cls):
        raise NotImplementedError

    @classmethod
    def in_(cls):
        raise NotImplementedError

    @classmethod
    def on(cls):
        raise NotImplementedError

    @classmethod
    def positioned(cls):
        raise NotImplementedError

    @classmethod
    def rotated(cls):
        raise NotImplementedError

    @classmethod
    def store(cls):
        raise NotImplementedError

    @classmethod
    def summon(cls):
        raise NotImplementedError

    @classmethod
    def if_(cls, condition_value, condition_type):
        """
        Alias for Condition(...)
        """
        return Condition(condition_value, condition_type)

    @classmethod
    def unless(cls, condition_value, condition_type):
        """
        Alias for ~Condition(...)
        """
        return ~Condition(condition_value, condition_type)

class RawExecute(RawCommand):
    NAME = 'execute'

    @staticmethod
    def _gen_tokens(subs: List[ExecuteSub | Condition], cmd: TokensRef | TokensContainer) -> TokensContainer:
        return [token for sub in subs for token in sub.tokenize()] + cmd.single_line_tokenize()

class Advancement(RawCommand):
    NAME = 'advancement'

    @staticmethod
    def _tokenize_sub(advancement, criterion=None, parents=False, children=False):
        if advancement == '*':
            return [CommandKeywordToken('everything')]
        elif parents and children:
            return [CommandKeywordToken('through'), advancement]
        elif parents:
            return [CommandKeywordToken('until'), advancement]
        elif children:
            return [CommandKeywordToken('from'), advancement]
        else:
            if criterion:
                return [CommandKeywordToken('only'), advancement, criterion]
            else:
                return [CommandKeywordToken('only'), advancement]

    @classmethod
    def grant(cls, target: Selector, advancement: Literal['*'] | ResourceLocation, criterion=None, parents=False, children=False):
        return cls(CommandKeywordToken('grant'), target, *cls._tokenize_sub(advancement, criterion, parents, children))

    @classmethod
    def revoke(cls, target: Selector, advancement: Literal['*'] | ResourceLocation, criterion=None, parents=False, children=False):
        return cls(CommandKeywordToken('revoke'), target, *cls._tokenize_sub(advancement, criterion, parents, children))
