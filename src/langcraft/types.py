from enum import StrEnum
from typing import Literal, Self
from termcolor import colored

from .debug_utils import print_debug
from .serialize import ResourceLocToken, Token, RawToken, SelectorToken, Serializable
from .minecraft_builtins.dimensions import _DimensionLiteral

class Int32(Token):
    MIN = -2**31
    MAX = 2**31 - 1
    def __init__(self, x: int):
        assert self.MIN <= x <= self.MAX
        self.x = x

    def __str__(self):
        return str(self.x)

class Selector(Serializable):
    def __init__(self, s = 's', **kwargs):
        self.token: SelectorToken = SelectorToken(s, **kwargs)

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

# class EntitySelector(Selector):
#     def __init__(self, **kwargs):
#         return Selector('e', **kwargs)
    
# class VarToken(Token): # TODO
#     def __init__(self, entity_ref: Selector, name: str):
#         self.entity_ref = SingleSelector(entity_ref)
#         self.name = name

#     def __str__(self):
#         return f'{self.entity_ref} {self.name}'

class _Relative:
    def __init__(self, val=None):
        self.val = val

    def __bool__(self):
        return False

    def __add__(self, val):
        if isinstance(val, _Relative):
            if val.val is None:
                # ~x + ~ = ~x
                # ~ + ~ = ~
                return self
            val_float = val.val
        else:
            # ~x + y = ~(x + y) to support intuitive +=
            val_float = val
            print_debug(f'interpreting {type(val)}({val}) as _Relative for _Relative.__add__')

        return _Relative((0 if self.val is None else self.val) + val_float)

    def __radd__(self, val):
        # self is not _Relative; return float
        # x + ~y = (x + y)
        return val + (0 if self.val is None else self.val)
    
    def __neg__(self):
        self.val = -self.val

    def __sub__(self, val):
        return self + -val
    
    @staticmethod
    def join(val0, val1):
        if isinstance(val1, _Relative):
            return val0 + val1
        # ~x join y = y to support optimization of repeated teleports
        return val1
    
    def __str__(self):
        if self.val is not None:
            return '~' + str(self.val)
        return '~'

class Pos(Serializable):
    """
    Class for relative coordinates for `minecraft:vec3`.
    """
    def __init__(self, x=_Relative(), y=_Relative(), z=_Relative(), _type=None):
        """
        Defines positions, e.g. ~ ~1 ~
        """
        self._type = _type
        self.vec3 = x, y, z
    
    @classmethod
    def relative(cls, x=0, y=0, z=0):
        """
        Defines relative positions, e.g. ~ ~1 ~
        """
        return cls(x, y, z, _type='~')

    @classmethod
    def angular(cls, left=0, up=0, forward=0):
        """
        Defines relative angular positions, e.g. ^ ^ ^5
        """
        return cls(left, up, forward, _type='^')
    
    def __add__(self, pos: Self) -> Self:
        assert self._type != '^' and pos._type != '^'
        
        return Pos(*(x0 + x1 for x0, x1 in zip(self.vec3, pos.vec3)))
    
    def join(self, pos: Self) -> Self:
        if self._type == '^' or pos._type == '^':
            raise TypeError('Invalid type for joining positions: angular')
        
        return Pos(*(_Relative.join(x0, x1) for x0, x1 in zip(self.vec3, pos.vec3)))

    def __str__(self):
        if self._type is None:
            return ' '.join(str(coord) for coord in self.vec3)
        else:
            return ' '.join(f'{self._type}{coord if coord else ''}' for coord in self.vec3)
        
class Loc(Pos):
    def __init__(self, x=0, y=0, z=0):
        """
        Alias for Pos.relative(x, y, z)
        """
        super().__init__(x, y, z, _type='~')

class Heightmap(StrEnum):
    surface = 'WORLD_SURFACE'
    ocean_floor = 'OCEAN_FLOOR'
    motion_blocking = 'MOTION_BLOCKING'
    motion_blocking_no_leaves = 'MOTION_BLOCKING_NO_LEAVES'


class Rot(Serializable):
    """
    Class for defining `minecraft:rotation`
    """
    def __init__(self, yaw=_Relative(), pitch=_Relative(), relative=False):
        """
        Defines an absolute rotation in degrees

        yaw: 0.0 is south (+Z), 90.0 is west (-X), 180.0==-180.0 is north (-Z), -90.0 is east (+X)
        pitch: -90.0 is down (-Y), 90.0 is up (+Y)
        """
        if isinstance(yaw, _Relative):
            self.yaw = yaw
        else:
            self.yaw = (yaw + 180) % 360 - 180
        if not isinstance(pitch, _Relative):
            assert -90 <= pitch <= 90
        self.pitch = pitch
        self.relative = relative

    def __add__(self, yaw=0, pitch=0):
        return Pos(self.yaw + yaw, self.pitch + pitch)

    def __str__(self):
        if self.relative:
            return f'~{self.yaw if self.yaw else ''} ~{self.pitch if self.pitch else ''}'
        else:
            return f'{self.yaw} {self.pitch}'

class ResourceLocation(Serializable):
    def __init__(self, namespace, path):
        self.token: ResourceLocToken = ResourceLocToken(namespace, path)

class Dimension(ResourceLocation):
    def __init__(self, dimension_name: _DimensionLiteral):
        """
        Type for a builtin minecraft dimension
        """
        self.dimension_name = dimension_name

        super().__init__('minecraft', [dimension_name])

    def external_ref(self, namespace, dimension_path) -> Self:
        """
        Reference a dimension from any namespace
        """
        if isinstance(dimension_path, str):
            dimension_path = dimension_path.split('/')
        super().__init__(namespace, dimension_path)
        return self

class _Relation(Serializable):
    def __init__(self,
                 relation: 
                    Literal['attacker'] | 
                    Literal['controller'] |
                    Literal['leasher'] |
                    Literal['origin'] |
                    Literal['owner'] |
                    Literal['passengers'] |
                    Literal['target'] |
                    Literal['vehicle']
                 ):
        self.relation = relation

    def __str__(self):
        return self.relation
