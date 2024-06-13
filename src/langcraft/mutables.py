from typing import Literal, Optional

from .base import Fun, FunStatement, Statement, Block
from .types import _Relation, Dimension, Selector, Pos, Rot, _Relative, SingleSelector, Heightmap
from .commands import RawExecute, ExecuteSub, Teleport, Kill
from .minecraft_builtins.dimensions import _DimensionLiteral

class _EntityRelative(_Relative):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity

class Entity:
    def __init__(self, selector: Selector):
        self.selector = selector
        self.as_selector: Literal['self'] | Selector | None = 'self'
        self.at_target: Selector | None = Selector()
        self.positioned = self.rotated = self.dimension = None
        self.at_heightmap: Optional[Heightmap] = None
        self.on_relation: Optional[_Relation] = None
    
    def as_parent(self):
        self.as_selector = None
        self.at = self.selector()
        return self

    def at_parent(self):
        self.at_target = None
        return self

    def at(self,
           at_target: Selector = Selector(),
           pos: Pos | Selector | None = None,
           rot: Rot | Selector | None = None,
           on: Heightmap | None = None):
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
                subs.append(ExecuteSub.as_(self.selector))
            case 'at':
                subs.append(ExecuteSub.at(self.selector))
            case 'both':
                subs.append(ExecuteSub.as_(self.selector))
                subs.append(ExecuteSub.at(Selector()))  # as <selector> at @s
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
        self.old_selector = self.selector
        self.selector = SingleSelector()
        return self

    # position and rotation
    def teleport(self, loc: Pos = Pos(), *rotation_args):
        Teleport(self.selector, loc, *rotation_args)
    @property
    def pos(self):
        return Pos()
    @pos.setter
    def pos(self, pos_: Pos):
        Teleport(self.selector, pos_)
    @property
    def x(self):
        return _EntityRelative(self)
    @x.setter
    def x(self, x_):
        Teleport(self.selector, Pos(x=x_))
    @property
    def y(self):
        return _EntityRelative(self)
    @y.setter
    def y(self, y_):
        Teleport(self.selector, Pos(y=y_))
    @property
    def z(self):
        return _EntityRelative(self)
    @z.setter
    def z(self, z_):
        Teleport(self.selector, Pos(z=z_))
    @property
    def yaw(self):
        return _EntityRelative(self)
    @yaw.setter
    def yaw(self, yaw_):
        Teleport(self.selector, Rot(yaw=yaw_))
    @property
    def pitch(self):
        return _EntityRelative(self)
    @pitch.setter
    def pitch(self, pitch_):
        Teleport(self.selector, Rot(pitch=pitch_))

    def kill(self):
        Kill(self.selector)
    
    def __exit__(self, *args):
        self.execute_as_fun.__exit__()
        self.selector = self.old_selector
        # TODO: could dynamically decide if just as_ or just at are necessary 
        subs = []
        if self.as_selector == 'self':
            subs.append(ExecuteSub.as_(self.selector))
        elif self.as_selector:
            subs.append(ExecuteSub.as_(self.as_selector))
        if self.at_target:
            subs.append(ExecuteSub.at(self.at_target))
        
        if self.dimension:
            subs.append(ExecuteSub.in_(self.dimension))
        if self.positioned:
            subs.append(ExecuteSub.positioned(self.positioned))
        if self.rotated:
            subs.append(ExecuteSub.rotated(self.rotated))
        if self.at_heightmap:
            subs.append(ExecuteSub.positioned(self.at_heightmap))
        
        
        Statement(RawExecute.as_cmds(subs, Block(FunStatement(self.execute_as_fun, attach_local_refs=True))))
