from typing import Literal, Optional

from langcraft.serialize import SelectorToken

from .base import Fun, FunStatement, Statement, Block
from .types import _SELECTOR_TYPE, _Relation, Dimension, _SelectorBase, Pos, Rot, _Relative, _SingleSelectorBase, Heightmap
from .commands import RawExecute, ExecuteSub, Teleport, Kill
from .minecraft_builtins.dimensions import _DimensionLiteral

class _EntityRelative(_Relative):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity

def s(**selector_kwargs):
    """
    TODO Decorator function for SelfSelector classes
    """
    def f(funct):
        funct()
    return f

class Entities(_SelectorBase):
    def __init__(self,
                 selector_type: _SELECTOR_TYPE = 'e',
                 **selector_kwargs
                 ):
        super().__init__(selector_type, **selector_kwargs)
        # self.token: SelectorToken  # from super().__init__(...)
        self.as_selector: Literal['self'] | _SelectorBase | None = 'self'
        self.at_target: _SelectorBase | Pos | Rot | None = _SelectorBase()
        self.positioned = self.rotated = self.dimension = None
        self.at_heightmap: Optional[Heightmap] = None
        self.on_relation: Optional[_Relation] = None
    
    def as_parent(self):
        self.as_selector = None
        self.at_target = self
        return self

    def at_parent(self):
        self.at_target = None
        return self

    def at(self,
           at_target: _SelectorBase | Pos | Rot = _SelectorBase(),
           pos: Pos | _SelectorBase | None = None,
           rot: Rot | _SelectorBase | None = None,
           on: Heightmap | None = None):
        """
        If at_target is not Selector(), the parent's position, rotation, and dimension are used except where otherwise specified
        """
        self.at_target = at_target
        self.positioned = pos
        self.rotated = rot
        self.at_heightmap = on
        return self

    def in_(self, dim: Dimension | _DimensionLiteral):
        if isinstance(dim, Dimension):
            self.dimension = dim
        else:
            self.dimension = Dimension(dim)
        return self

    def __call__(self, funct: Fun, mode: Literal['as'] | Literal['at'] | Literal['both'] = 'both'):
        """
        Call functions as/at this entity outside of a with expression
        """
        subs = []
        match mode:
            case 'as':
                subs.append(ExecuteSub.as_(self.token))
            case 'at':
                subs.append(ExecuteSub.at(self.token))
            case 'both':
                subs.append(ExecuteSub.as_(self.token))
                subs.append(ExecuteSub.at(_SelectorBase()))  # as <selector> at @s
        RawExecute(subs, Block(FunStatement(funct, attach_local_refs=True)))

    @property
    def attacker(self):
        self.on_relation = _Relation('attacker')
        return self
    @property
    def controller(self):
        self.on_relation = _Relation('controller')
        return self
    @property
    def leasher(self):
        self.on_relation = _Relation('leasher')
        return self
    @property
    def origin(self):
        self.on_relation = _Relation('origin')
        return self
    @property
    def owner(self):
        self.on_relation = _Relation('owner')
        return self
    @property
    def passengers(self):
        self.on_relation = _Relation('passengers')
        return self
    @property
    def target(self):
        self.on_relation = _Relation('target')
        return self
    @property
    def vehicle(self):
        self.on_relation = _Relation('vehicle')
        return self

    def __enter__(self):
        self.execute_as_fun = Fun().__enter__()
        self.old_token = self.token
        self.token = _SingleSelectorBase().token
        return self

    # position and rotation
    def teleport(self, loc: Pos = Pos(), *rotation_args):
        Teleport(self, loc, *rotation_args)
    def propel(self, x: int):
        Teleport(self, Pos.angular(forward=x))
    @property
    def pos(self):
        return Pos()
    @pos.setter
    def pos(self, pos_: Pos):
        Teleport(self, pos_)
    @property
    def x(self):
        return _EntityRelative(self)
    @x.setter
    def x(self, x_):
        Teleport(self, Pos(x=x_))
    @property
    def y(self):
        return _EntityRelative(self)
    @y.setter
    def y(self, y_):
        Teleport(self, Pos(y=y_))
    @property
    def z(self):
        return _EntityRelative(self)
    @z.setter
    def z(self, z_):
        Teleport(self, Pos(z=z_))
    @property
    def yaw(self):
        return _EntityRelative(self)
    @yaw.setter
    def yaw(self, yaw_):
        Teleport(self, Rot(yaw=yaw_))
    @property
    def pitch(self):
        return _EntityRelative(self)
    @pitch.setter
    def pitch(self, pitch_):
        Teleport(self, Rot(pitch=pitch_))

    def kill(self):
        Kill(self)
    
    def __exit__(self, *args):
        self.execute_as_fun.__exit__()
        self.token = self.old_token
        # TODO: could dynamically decide if just as_ or just at are necessary
        subs = []
        if self.as_selector == 'self':
            subs.append(ExecuteSub.as_(self))
        elif self.as_selector:
            subs.append(ExecuteSub.as_(self.as_selector))
        if self.dimension:
            subs.append(ExecuteSub.in_(self.dimension))
        if self.at_target:
            if isinstance(self.at_target, _SelectorBase):
                subs.append(ExecuteSub.at(self.at_target))
            if isinstance(self.at_target, Pos):
                subs.append(ExecuteSub.positioned(self.at_target))
            if isinstance(self.at_target, Rot):
                subs.append(ExecuteSub.rotated(self.at_target))
        if self.positioned:
            subs.append(ExecuteSub.positioned(self.positioned))
        if self.rotated:
            subs.append(ExecuteSub.rotated(self.rotated))
        if self.at_heightmap:
            subs.append(ExecuteSub.positioned(self.at_heightmap))
        
        
        Statement(RawExecute.as_cmds(subs, [FunStatement(self.execute_as_fun, attach_local_refs=True)]))

class Self(Entities):
    def __init__(self,
                 **selector_kwargs
                 ):
        super().__init__('s', **selector_kwargs)
