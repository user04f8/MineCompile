from copy import copy, deepcopy
from enum import Enum, auto
from typing import List, Optional, Self, Literal, Iterable

from .base import Statement, Fun, Block, FunStatement
from .serialize import *
from .types import *
from .debug_utils import *
from .types import _Relative

class ConditionType(Enum):
    STR = auto()
    
    FALSE = auto()
    TRUE = auto()
    
    ALL = auto()
    OR = auto()
    ANY = auto()

    BIOME = auto()
    BLOCK = auto()
    BLOCKS = auto()
    BLOCK_DATA = auto()
    ENTITY_DATA = auto()
    STORAGE_DATA = auto()
    DIMENSION = auto()
    FUNCTION = auto()
    ENTITY = auto()


class Condition:
    def __init__(self, value: str | List[Self] = '', condition_type: ConditionType = ConditionType.STR):
        self.condition_type = condition_type
        self.value = value
        self.inverted = False

        # match self.condition_type:
        #     case ConditionType.OR:
        #         assert not any(condition.condition_type == ConditionType.OR for condition in self.value), "ERROR: Condition not in disjunctive normal form (DNF)"
        #     case ConditionType.ALL:
        #         assert not any(condition.condition_type in {ConditionType.OR, ConditionType.ALL} for condition in self.value), "ERROR: Condition not in disjunctive normal form (DNF)"


    @property
    def always_true(self):
        return self.condition_type == ConditionType.TRUE
    
    @property
    def always_false(self):
        return self.condition_type == ConditionType.FALSE
    
    def __invert__(self) -> Self:
        inv_self = deepcopy(self)

        if inv_self.always_true:
            inv_self.condition_type = ConditionType.FALSE
        elif inv_self.always_false:
            inv_self.condition_type = ConditionType.TRUE
        elif inv_self.condition_type in {ConditionType.OR, ConditionType.ALL}:
            inv_self.value = [~sub_condition for sub_condition in inv_self.value]  # De Morgan's laws
        else:
            inv_self.inverted = not inv_self.inverted
        return inv_self

    def __and__(self, c: 'Condition') -> 'Condition':
        def or_like(c: Condition):
            return c.condition_type in {ConditionType.OR, ConditionType.ANY}
        def to_dnf(c1s: Condition, c2s: Condition):
            assert or_like(c1s), "Incorrect use of to_dnf"
            if not or_like(c2s):
                c2s = Condition(value=[c2s], condition_type=ConditionType.OR)
            dnf_clauses = []
            for c1 in c1s.value:
                for c2 in c2s.value:
                    if c1.condition_type == ConditionType.ALL:
                        if c2.condition_type == ConditionType.ALL:
                            dnf_clauses.append(Condition(value=c1.value + c2.value, condition_type=ConditionType.ALL))
                        else:
                            dnf_clauses.append(Condition(value=c1.value + [c2], condition_type=ConditionType.ALL))
                    else:
                        if c2.condition_type == ConditionType.ALL:
                            dnf_clauses.append(Condition(value=[c1] + c2.value, condition_type=ConditionType.ALL))
                        else:
                            dnf_clauses.append(Condition(value=[c1, c2], condition_type=ConditionType.ALL))
            return dnf_clauses

        if self.always_false or c.always_true:
            return self
        elif self.always_true or c.always_false:
            return c
        elif self.condition_type == ConditionType.ALL:
            if c.condition_type == ConditionType.ALL:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        elif or_like(self):
            return Condition(condition_type=ConditionType.OR, value=to_dnf(self, c))
        elif or_like(c):
            return Condition(condition_type=ConditionType.OR, value=to_dnf(c, self))
        else:
            return Condition(condition_type=ConditionType.ALL, value=[self, c])
        
    def __add__(self, c: 'Condition') -> 'Condition':
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

    def __or__(self, c: 'Condition') -> 'Condition':
        if self.always_false or c.always_true:
            return c
        elif self.always_true or c.always_false:
            return self
        if self.condition_type == ConditionType.OR:
            if c.condition_type == ConditionType.OR:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        return Condition(condition_type=ConditionType.OR, value=[self, c])

    def tokenize(self) -> List[Token]:
        match self.condition_type:
            case ConditionType.ANY:
                return [Choice(*(c.tokenize() for c in self.value))]
            case ConditionType.OR:
                return [Choice(*(([CommandKeywordToken('unless'), CheckFlagToken(self.flag)] if i > 0 else []) + c.tokenize() for i, c in enumerate(self.value)))]
                # SIMPLE CASES ONLY:
                # added_conds = []
                # out = []
                # for c in self.value:
                #     out.append(
                #         (
                #             c & Condition([~d for d in added_conds], ConditionType.ALL)
                #         ).tokenize()
                #     )
                #     added_conds.append(c)
                # return [Choice(*out)]
            case ConditionType.ALL:
                return [token for condition in self.value for token in condition.tokenize()]
            case _:
                match self.condition_type:
                    case ConditionType.STR:
                        tokens = [RawToken(self.value)]
                return [(CommandKeywordToken('unless') if self.inverted else CommandKeywordToken('if')), *tokens]
            
    def pre_tokenize(self) -> Optional[Flag]:
        match self.condition_type:
            case ConditionType.OR:
                self.flag = Flag()
                return self.flag
            case _:
                return None

class ExecuteSub:
    def __init__(self, subcmd: str, *args: Token):
        self.subcmd = CommandKeywordToken(subcmd)
        self.tokens = args

    def tokenize(self) -> List[Token]:
        return [self.subcmd, *self.tokens]
    
    def pre_tokenize(self):
        return None

    @classmethod
    def align(cls):
        raise NotImplementedError

    @classmethod
    def anchored(cls):
        raise NotImplementedError

    @classmethod
    def as_(cls, selector: Selector):
        return cls('as', selector)

    @classmethod
    def at(cls, selector: Selector):
        return cls('at', selector)

    @classmethod
    def facing(cls):
        raise NotImplementedError

    @classmethod
    def in_(cls, dim: Dimension):
        return cls('in', dim)

    @classmethod
    def on(cls):
        raise NotImplementedError

    @classmethod
    def positioned(cls, pos: Pos | Selector | Heightmap):
        if isinstance(pos, Pos):
            return cls('positioned', pos)
        elif isinstance(pos, Selector):
            return cls('positioned', CommandKeywordToken('as'), pos)
        else: # isinstance(pos, Heightmap)
            return cls('positioned', CommandKeywordToken('over'), MiscToken(pos))

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

# special commands:

class RawExecute(Statement):
    def __init__(self, subs: List[ExecuteSub | Condition], run_block: Block = Block(), add=True):
        cmds = self.as_cmds(subs, run_block)
        super().__init__(cmds, add=add)

    @staticmethod
    def as_cmds(subs: List[ExecuteSub | Condition], run_block: Block = Block()):
        flags = [sub.pre_tokenize() for sub in subs]
        cmds = [TokensContainer(ResetFlagToken(flag)) for flag in flags if isinstance(flag, Flag)]
        set_flags = [Statement(SetFlagToken(flag), add=False) for flag in flags if isinstance(flag, Flag)]
        execute_block = Block(*(set_flags + run_block.statements))
        if len(execute_block) == 0:
            block_tokens = []
        elif len(execute_block) == 1:
            block_tokens = [CommandKeywordToken('run')] + execute_block.single_line_tokenize()
        else:
            block_tokens = [CommandKeywordToken('run'), Fun._wrap_tokens(execute_block.tokenize())]
        cmds.append(TokensContainer(
            CommandNameToken('execute'),
            *([token for sub in subs for token in sub.tokenize()] + block_tokens)
        ))
        return cmds

# common commands:

class Teleport(Statement):
    """
        command syntax:
        
        teleport <destination>
        teleport <targets> <destination> 
        teleport <location>
        teleport <targets> <location>
        teleport <targets> <location> <rotation>
        teleport <targets> <location> facing <facingLocation>
        teleport <targets> <location> facing entity <facingEntity> [<facingAnchor>]
    """
    def __init__(self, /, *args, add=True):
        # args = [arg for arg in args if arg is not None] # trim kwarg=None to defaults
        self.simple = False
        if len(args) == 1 and isinstance(args[0], SingleSelector):
            tokens = args
        else:
            if args and isinstance(args[0], Selector):
                self.target, *args = args
            else:
                self.target = Selector()
            if args and isinstance(args[0], Pos):
                self.loc, *args = args
            else:
                self.loc = Pos()
            tokens = [self.target, self.loc]
            if args and isinstance(args[0], Rot):
                rot, *args = args
                tokens.append(rot)
            elif args and isinstance(args[0], Pos):
                facing, *args = args
                tokens += [CommandKeywordToken('facing'), facing]
            elif args and isinstance(args[0], Pos):
                facing_entity, *args = args
                if args and (args[0] == 'eyes' or args[0] == 'feet'):
                    tokens += [CommandKeywordToken('facing entity'), facing_entity, CommandKeywordToken(args.pop())]
                else:
                    tokens += [CommandKeywordToken('facing entity'), facing_entity]
            else:
                self.simple = True
            if len(args) > 0:
                raise TypeError(f'invalid args for Teleport: {args}')
        # print(tokens)
        cmds = [CommandNameToken('tp'), *tokens]
        super().__init__(cmds, add=add)
    
    def join_with_cmd(self, cmd):
        if isinstance(cmd, Teleport):
            if self.target != cmd.target or not self.simple or not cmd.simple:
                return
            return Teleport(self.target, self.loc.join(cmd.loc), add=False)

class Kill(Statement):
    def __init__(self, selector: Optional[Selector] = None, add=True):
        cmds = [CommandNameToken('kill')]
        if selector is not None:
            cmds.append(selector)
        super().__init__(cmds, add=add)

# other commands:

class RawCommand(Statement):
    NAME: str

    def __init__(self, *args, add=True, **kwargs):
        cmds = [self._as_cmds(*args, **kwargs)]
        # if isinstance(tokens, str):
        #     tokens = [StrToken(token) for token in tokens.split()]
        super().__init__(cmds, add=add)

    def _as_cmds(self, *tokens: Token) -> TokensContainer:
        # cmds = cls(*args, add=False).get_cmds()
        # assert len(cmds) == 0
        # return cmds[0]
        return TokensContainer(CommandNameToken(self.NAME), *tokens)


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

...  # TODO

