from typing import Dict, Literal, Optional

from langcraft.json_utils import JSON
from langcraft.serialize import SelectorToken

from .base import Fun, Statement, Block, WithStatement
from .types import _SELECTOR_TYPE, _Relation, Dimension, _SelectorBase, Pos, ResourceLocation, Rot, _Relative, _SingleSelectorBase, Heightmap, _SliceType
from .commands import RawExecute, ExecuteSub, Teleport, Kill
from .minecraft_builtins import _Entities
from .dimension import _Dimension

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
                 type: _Entities = None,
                 name: str = None,
                 predicate: 'Predicate' = None, # TODO add Predicate type # type: ignore
                 nbt: JSON = None,
                 selected_item: JSON = None,
                 distance: float = None,
                 x: float = None, y: float = None, z: float = None, # xyz start
                 dx: float = None, dy: float = None, dz: float = None, # (xyz end) - (xyz start) for bbox
                 x_rotation: _SliceType = None, y_rotation: _SliceType = None,
                 scores: Dict[str, _SliceType] = None,
                 tag: str = None,
                 team: str = None,
                 limit: int = None,
                 sort: Literal['nearest', 'furthest', 'random', 'arbitrary'] = None,
                 level: _SliceType = None,
                 gamemode: Literal['spectator', 'survival', 'creative', 'adventure'] = None,
                 advancements: Dict[ResourceLocation, bool | Dict[str, bool]] = None
                 ):
        scores = None if scores is None else ('{' + ','.join(f'{k}={v}' for k, v in scores.items()) + '}' if isinstance(scores, dict) else scores)
        if selected_item:
            assert nbt is None
            nbt = JSON(selected_item=selected_item)
        super().__init__(selector_type,
                         name=name,
                         type=type,
                         predicate=predicate,
                         nbt=nbt,
                         distance=distance,
                         x=x, y=y, z=z,
                         dx=dx, dy=dy, dz=dz,
                         x_rotation=x_rotation, y_rotation=y_rotation,
                         scores=scores,
                         tag=tag,
                         team=team,
                         limit=limit,
                         sort=sort,
                         level=level,
                         gamemode=gamemode,
                         advancements=advancements)
        # self.token: SelectorToken  # from super().__init__(...)
        self.as_selector: Literal['self'] | _SelectorBase | None = 'self'
        self.at_target: _SelectorBase | Pos | Rot | None = _SelectorBase()
        self.positioned = self.rotated = self.dimension = None
        self.at_heightmap: Optional[Heightmap] = None
        self.on_relation: Optional[_Relation] = None
        self.anchor: Optional[Literal['eyes', 'feet']] = None  # default is feet
    
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

    def in_(self, dim: Dimension | _Dimension):
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
        RawExecute.conditional_fun(subs, funct)

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

    @property
    def eyes(self):
        self.anchor = 'eyes'
        return self
    @property
    def feet(self):
        self.anchor = 'feet'
        return self

    def __enter__(self):
        self.execute_as_fun = Fun().__enter__()
        self.old_token = self.token
        self.token = _SingleSelectorBase().token
        return self

    # position and rotation
    def teleport(self, loc: Pos = Pos(), *rotation_args):
        Teleport(self, loc, *rotation_args)
    def propel(self, forward: int):
        Teleport(self, Pos.angular(forward=forward))
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
        if self.anchor:
            subs.append(ExecuteSub.anchored(self.anchor))
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
        
        RawExecute.conditional_fun(subs, self.execute_as_fun)

class Self(Entities):
    def __init__(self,
                 **selector_kwargs
                 ):
        super().__init__('s', **selector_kwargs)

class Summon(WithStatement):
    def __init__(self,    
                 entity_name: _Entities
                 ):
        self.entity_name = entity_name
        
    def __enter__(self):
        super().__enter__()
        return Self()
    
    def __call__(self, *statements: Statement):
        RawExecute([ExecuteSub.summon(self.entity_name)], list(statements))
