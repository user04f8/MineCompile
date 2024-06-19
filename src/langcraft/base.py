from copy import copy
from enum import Enum
from typing import Callable, List, Optional, Tuple

from langcraft.serialize import TokensContainer

from .globals import GLOBALS, Ref, RefFlags
from .debug_utils import *
from .serialize import *
from .types import Int32, JSONText


class Namespace:
    def __init__(self, name: str, full_path: Optional[List[str]] = None):
        self.old_name = GLOBALS.namespace
        self.name = name
        self.old_path = GLOBALS.path
        self.new_path = full_path

    def __enter__(self):
        GLOBALS.set_namespace(self.name, self.new_path)

    def __exit__(self, *args):
        GLOBALS.set_namespace(self.old_name, self.old_path)

class Pathspace:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        GLOBALS.enter_path(self.name)

    def __exit__(self, *args):
        GLOBALS.exit_path(self.name)


class ArgType(Enum):
    INT = 1
    # TUPLE = 10
    UNKOWN = -1

    @staticmethod
    def from_type(t):
        return {
            int: ArgType.INT,
        }.get(t, ArgType.UNKOWN)

    @staticmethod
    def infer(x):
        match x:
            # case tuple(xs) | list(xs):
            #     self.type = SimpleValType.TUPLE
            #     self.types = tuple(ValType(x) for x in xs)
            case int(x):
                return ArgType.INT
            case _:
                return ArgType.UNKOWN
    
    def cast(self, x):
        match self:
            case ArgType.INT:
                return Int32(x)
            case _:
                raise TypeError(f"Type {self} doesn't support input {x}")
            
# class ValueRef:
    # def __init__(self, x, type: Optional[ArgType]):
    #     if type is None:
    #         self.type = ArgType.infer(x)
    #     else:
    #         x = type.cast(x)
    #         self.type = type
    #     self.x = x

class Arg(TokensRef):
    def __init__(self, ident: int, type_: ArgType):
        self.ident = ident
        if isinstance(type_, ArgType):
            self.type_ = type_
        else:
            raise TypeError()
        self.static_value = None

    def assign(self, val):
        raise NotImplementedError()

    def get_cmds(self):
        return [TokensContainer(ArgToken(self.ident))]

class Args:
    def __init__(self, fun=None):
        self.args = [Arg(i, type_) for i, type_ in enumerate(fun.in_types)]

    def __iter__(self):
            return self.args.__iter__()

class MetaArg(Token):
    def __init__(self, id: int):
        self.id = id

    def assign(self, val):
        self.val = val

    def __str__(self):
        if hasattr(self, 'val'):
            return str(self.val)
        else:
            return f'$meta_arg:{self.id}'

class MetaArgs:
    def __init__(self):
        self.len = 0
        self.args = []

    def __iter__(self):
        return self
    
    def __next__(self):
        arg = MetaArg(self.len)
        self.args.append(arg)
        self.len += 1
        return arg

class Partial:
    def __init__(self, inner_fun: Callable[[str], Callable]):
        self.inner_fun = inner_fun
        
    def __enter__(self):
        self.inner_fun_name = GLOBALS.gen_function_name()
        self.f = self.inner_fun(name=self.inner_fun_name).__enter__()
        if isinstance(self.f, tuple):
            self.f, self.f_args = self.f
        else:
            self.f_args = None
        self.meta_args = MetaArgs()
        def h(*meta_args):
            for meta_arg, arg in zip(self.meta_args.args, meta_args):
                meta_arg.assign(arg)
            def g(*args):
                self.inner_fun(name=self.inner_fun_name)(*args)
            return g
        def get_args(n: int = None):
            if n is None:
                return next(self.meta_args)
            else:
                return [next(self.meta_args) for _ in range(n)]
        if self.f_args:
            return (h, self.f_args), get_args
        else:
            return h, get_args
    
    def __exit__(self, *args):
        self.f.__exit__()

class Statement(TokensRef):
    def __init__(self, cmds: str | Arg | Token | TokensContainer | List[Token] | List[TokensContainer], *, add=True):
        if isinstance(cmds, str):
            cmds = cmds.strip()
            if '\n' in cmds:
                cmds = cmds.split('\n')
                for cmd in cmds:
                    Statement(cmd)
                return
            if cmds[0] == '/':
                cmds = cmds[1:]
            self.cmds = [TokensContainer(RawToken(cmds))]
        elif isinstance(cmds, Arg):
            self.cmds = cmds.get_cmds()
        elif isinstance(cmds, Token):
            self.cmds = [TokensContainer(cmds)]
        elif isinstance(cmds, TokensContainer):
            self.cmds = [cmds]
        elif isinstance(cmds, List | Tuple):
            if len(cmds) == 0:
                self.cmds = []
            elif isinstance(cmds[0], Token):
                self.cmds = [TokensContainer(*cmds)]
            elif isinstance(cmds[0], TokensContainer):
                self.cmds = cmds
            else:
                print_warn(f'Unrecognized {type(cmds)}: {cmds}')
                self.cmds = cmds
        else:
            raise TypeError(f"Invalid type for Statement cmds {type(cmds)}")

        if add:
            self.idx = GLOBALS.add_statement(self)
        else:
            self.idx = None

    def get_cmds(self) -> List[TokensContainer]:
        return self.cmds
    
    def clear(self):
        if self.idx is not None:
            GLOBALS.clear_cmd(self.idx)

class DebugStatement(Statement):
    def __init__(self, msg: str = 'here', include_selector=True, scores=[]):
        # json = {"text": f"({GLOBALS.namespace}:{'/'.join(GLOBALS.path)}) {msg}"}
        json_text = JSONText(f"({GLOBALS.namespace}:{'/'.join(GLOBALS.path)})", color='gray')
        if include_selector:
            json_text += JSONText(' <') + JSONText(selector="@s", color='aqua') + JSONText('>', color='gray')

        json_text += JSONText(' ' + msg)

        for score in scores:
            json_text += JSONText(f'\n{score}=') + JSONText(score_name="@s", score_objective=score)

        super().__init__(f'tellraw @a {json_text}')

        # super().__init__(f'tellraw @a {JSONText(text=f"({GLOBALS.namespace}:{'/'.join(GLOBALS.path)}) {msg}", hover_event=dict(action="show_text", contents=JSONText(selector="@s")))}')

class Pass(Statement):
    def __init__(self, add=True):
        if add:
            self.idx = GLOBALS.add_statement(self)
        else:
            self.idx = None

    def get_cmds(self) -> List[TokensContainer]:
        return [TokensContainer(RawToken(''))]

class WithStatement(Statement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unwrapped = False
        GLOBALS.in_with = True # ensure inline __call__s still generate refs properly

    def __enter__(self):
        GLOBALS.blocks.append(self)
        self.args_from_global = []

    def add_statement(self, statement: Statement):
        self.args_from_global.append(statement)

    def __exit__(self, *args):
        GLOBALS.blocks.pop()
        GLOBALS.in_with = False
        self(*self.args_from_global)
        

    def _unwrap_statement(self, ref: Ref, single_line_tokens: List[Token], _ExecuteContainer: type):
        for cmd in self.cmds:
            if isinstance(cmd, _ExecuteContainer):
                fun_token = cmd.get_fun_token()
                if fun_token is None:
                    print_warn(f'already unwrapped {ref}')
                else:
                    fun_path = GLOBALS.get_function_path(fun_token.namespace, fun_token.path)
                    if fun_path == ref[1]:
                        assert cmd._block_tokens != []
                        cmd._block_tokens[1:] = single_line_tokens
                        self._unwrapped = True

class Block(Statement):
    def __init__(self, *statements: Statement | str):
        self.statements = [(Statement(statement) if isinstance(statement, str) else statement) for statement in statements]

    def get_cmds(self) -> List[TokensContainer]:
        return [cmd for statement in self.statements for cmd in statement.get_cmds()]
    
    def cmds_to_global(self):
        for statement in self.statements:
            GLOBALS.add_statement(statement)
    
    def __len__(self):
        return len(self.statements)
    
    def clear(self):
        for statement in self.statements:
            statement.clear()

class FunStatement(Statement):
    def __init__(self, fun: 'Fun', attach_local_refs=False, ref_type: RefFlags = RefFlags.NONE):
        self.fun = fun
        self.cmds = [TokensContainer(FunctionToken(self.fun.namespace, self.fun.path))]
        self.idx = None
        if attach_local_refs:
            self.fun._attach_fun_ref(path=GLOBALS.get_function_path(), ref_type=ref_type)
    
    def __call__(self, *args):
        for fun_arg, arg in zip(self.fun.args, args):
            fun_arg.assign(arg)
        super().__init__(self.cmds, add=True)
        self.fun._attach_fun_ref(path=GLOBALS.get_function_path())

        # vals = (Value(val, type=in_type) for in_type, val in zip(self.fun.in_types, args))
        
        # if isinstance(self.fun.block.statements[0], ArgNames):
        #     funct_arg_names = self.fun.block.statements[0]
        #     self.fun.block.statements = self.fun.block.statements[1:]
        #     assignments = {funct_arg_name: val for funct_arg_name, val in zip(funct_arg_names, vals)}
        # else:
        #     assignments = {ArgNames.default(i): arg for i, arg in enumerate(args)}
        
        # for statement in self.fun.block.statements:
        #     pass


class Fun:
    def __init__(self, name: Optional[str] = None,
                # namespace: Optional[str] = None,
                # path: Optional[List[str]] = None
                 ):
        
        if name is None:
            self.name = GLOBALS.gen_function_name()
        else:
            self.name = name
        
        self.namespace = GLOBALS.namespace
        if self.name == '$self':
            # reference self
            self.path = GLOBALS.path
        else:
            self.path = GLOBALS.path + [self.name]
        
        self.inline = True
        self.inline_block = None        

        self.out_types: Tuple[ArgType] | ArgType | None = None
        self.in_types: Tuple[ArgType] | ArgType | None = None

        self.ref = None
        self.args = []
        # self.refs = set()

    def __str__(self):
        """
        Direct string conversion for easier passing around of functions
        NOTE: may break refs
        """
        return str(FunStatement(self, attach_local_refs=True).tokenize()[0])
    
    @classmethod
    def statement(cls, name: Optional[str] = None, namespace: Optional[str] = None, path: Optional[List[str]] = None) -> FunStatement:
        if namespace or path:
            with Namespace(namespace, path):
                return FunStatement(cls(name=name))
        elif name:
            return FunStatement(cls(name=name))
        else:
            # default to current function
            return FunStatement(cls(name='$self'))

    @classmethod
    def callable(cls, *in_types):
        return lambda name: Fun(name)[*in_types]

    def __class_getitem__(self, types: type | Tuple[type]):
        self.out_types = types
        # if isinstance(types, tuple):
        #     self.out_types = tuple(ArgType.from_type(t) for t in types)
        # else:
        #     self.out_types = ArgType.from_type(types)
        return self

    def __getitem__(self, types: type | Tuple[type]):
        self.in_types = types
        if isinstance(types, tuple):
            self.in_types = tuple(ArgType.from_type(t) for t in types)
        else:
            self.in_types = ArgType.from_type(types)
        return self
    
    def __enter__(self) -> Self | Tuple[Self, Arg] | Tuple[Self, Args]:
        self.inline = False
        GLOBALS.enter_path(self.name)
        assert self.namespace == GLOBALS.namespace
        assert self.path == GLOBALS.path
        # self.namespace = GLOBALS.namespace
        # self.path = copy(GLOBALS.path)  # need to copy or else since path is a List object this will be a reference

        self.parent = GLOBALS.fun
        GLOBALS.fun = self
        self.ref = self._gen_ref()
        # EmptyStatement()
        if self.in_types is None:
            return self
        elif isinstance(self.in_types, ArgType):
            self.args = [Arg(0, self.in_types)]
            return self, self.args
        else:
            self.args = [arg for arg in Args(self)]
            return self, self.args
        
    @staticmethod
    def _gen_ref(path=None) -> Tuple[str, str]:
        if path:
            return ('function', path)
        else:
            return ('function', GLOBALS.get_function_path())
    
    def __exit__(self, *args):
        GLOBALS.exit_path(self.name)
        GLOBALS.fun = self.parent
    
    def __call__(self, *args) -> FunStatement:
        if self.inline:
            if self.inline_block is None:
                print_debug(f'deprecated inline Fun {self.namespace}:{'/'.join(self.path)}')
                self.inline_block = Block(*args)
                self.inline_block.clear()

                fun_statement = FunStatement(self)
                # fun_statement.__call__(*args)
                return fun_statement
            else:
                raise ValueError('Function block already assigned')
        else:
            print_debug(f'implicit function->statement call {self.namespace}:{'/'.join(self.path)}')
            fun_statement = FunStatement(self)
            fun_statement.__call__(*args)
            return fun_statement
    
    @classmethod
    def _wrap_statements(cls, statements: List[Statement]) -> FunctionToken:
        caller_ref = cls._gen_ref()
        print_debug(f'_wrap_tokens call from {caller_ref}')

        with Pathspace(GLOBALS.gen_function_name()):
            for statement in statements:
                GLOBALS.add_statement(statement)
            print_debug(f'attaching ref to {caller_ref}: anon funct:')
            GLOBALS.ref_call(caller_ref, cls._gen_ref(), ref_type=RefFlags.EXECUTE)

            path = copy(GLOBALS.path)

        return FunctionToken(GLOBALS.namespace, path)
    
    def _attach_hook(self, hook: str):
        print_debug(f'attaching hook to {self.name}: {hook}')
        self._attach_ref(
            ('$extern', hook)
        )
        if hook not in GLOBALS.fun_hooks:
            GLOBALS.fun_hooks[hook] = {self}
        else:
            GLOBALS.fun_hooks[hook].add(self)

    def _attach_fun_ref(self, path: str, ref_type: RefFlags = RefFlags.NONE):
        self._attach_ref(self._gen_ref(path=path), ref_type=ref_type)
    
    def _attach_ref(self, caller_ref: Tuple[str, str], ref_type: RefFlags = RefFlags.NONE):
        print_debug(f'attaching ref to {caller_ref}: {self.name}')
        if GLOBALS.in_with:
            GLOBALS.ref_call(caller_ref, self.ref, ref_type=(ref_type | RefFlags.WITH_BLOCK))
        else:
            GLOBALS.ref_call(caller_ref, self.ref, ref_type=ref_type)
    
class PublicFun(Fun):
    def __init__(self, name: str):
        super().__init__(name=name)

    def __enter__(self):
        out = super().__enter__()
        self._attach_hook('$public')
        return out

class TickingFun(Fun):
    def __enter__(self):
        out = super().__enter__()
        self._attach_hook('#minecraft:tick')
        return out

class OnLoadFun(Fun):
    def __enter__(self):
        out = super().__enter__()
        self._attach_hook('#minecraft:load')
        return out

def fun(inner):
    """
    Decorator function to convert functions into Fun, e.g.:
    @fun
    def f():
        Statement('say hi')
    """
    with Fun() as f:
        inner()
    return f

def metafun(inner):
    """
    Decorator function to convert functions into meta-Fun supporting arguments, e.g.:
    @metafun
    def say(x):
        Statement(f'say {x}')
    """
    def wrapper(*args, **kwargs):
        with Fun() as f:
            inner(*args, **kwargs)
        return f()
    return wrapper


class caching_metafun:
    def __init__(self):
        self.caches = {}

    def __call__(self, inner):
        def wrapper(*args, **kwargs):
            frozen_kwargs = frozenset(kwargs.items())
            cache_key = (args, frozen_kwargs)
            if cache_key not in self.caches:
                with Fun() as f:
                    inner(*args, **kwargs)
                self.caches[cache_key] = f
            return self.caches[cache_key]()
        return wrapper

def lambda_metafun(inner):
    def wrapper(*args, **kwargs):
        with Fun() as f:
            inner(*args, **kwargs)
        return f
    return wrapper

# EXAMPLE USAGE:
# @lambda_metafun
# def lambda_tnt_line():
#     with Self().at(Pos.angular(forward=8)):
#         line(
#             lambda: Statement('summon tnt ~ ~1.8 ~'),
#             Condition(True),
#             50
#         )
#         Kill(Self())

# @public
# def tnt_laser():
#     Statement(f'execute summon marker run {lambda_tnt_line()}')


def public(func: str | Callable, metafun_args: list = [], metafun_kwargs: dict = {}):
    """
    Decorator function to make publically available function with name, e.g.
    @public('say_hi')
    @fun
    def f():
        Statement('say hi')

    Alternative equivalent usage for argument-free functions:
    @public
    def say_hi():
        Statement('say hi)
    """
    if isinstance(func, str):
        def outer_wrapper(inner: Fun):
            with PublicFun(func) as f:
                inner(*metafun_args, **metafun_kwargs)
            f()
        return outer_wrapper
    with PublicFun(func.__name__) as f:
        func(*metafun_args, **metafun_kwargs)
    f()
    return f

def _fun_subclass(fun_class: type):
    def outer_wrapper(inner):
        with fun_class() as f:
            inner()
        f()
        class wrapper:
            def __init__(self, f):
                self.f = f

            def __call__(self, *args, **kwargs):
                if args != () or kwargs != {}:
                    raise ValueError("Subclassed function from decorator doesn't support dynamic arguments")
                self.f()
        return wrapper(f)
    return outer_wrapper

fun.ticking = _fun_subclass(TickingFun)
fun.on_load = _fun_subclass(OnLoadFun)
