from __future__ import annotations

from typing import Dict, List, Literal, Optional

from langcraft.globals import GLOBALS
from langcraft.serialize import TokensContainer

from .json_utils import JSON
from .serialize import SelectorToken, TokensRef
from .base import Fun, Statement, Block, WithStatement, fun
from .serialize_types import _SELECTOR_TYPE, _Relation, Dimension, _SelectorBase, Pos, ResourceLocation, Rot, _Relative, _SingleSelectorBase, _PlayerSelectorBase, _SinglePlayerSelectorBase, Heightmap, _SliceType
from .commands import RawExecute, ExecuteSub, Teleport, Kill
from .minecraft_builtins import EntityType
from .dimension import _Dimension

class _EntityRelative(_Relative):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity

class Entities(_SelectorBase):
    def __init__(self,
                 selector_type: _SELECTOR_TYPE = 'e',
                 type: EntityType = None,
                 name: str = None,
                 predicate = None,  # TODO add Predicate type
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
        self.as_selector: Literal['self'] | _SelectorBase | None = 'self'
        self.at_target: _SelectorBase | Pos | Rot | None = _SelectorBase()
        self.positioned = self.rotated = self.dimension = None
        self.at_heightmap: Optional[Heightmap] = None
        self.on_relation: Optional[_Relation] = None
        self.anchor: Optional[Literal['eyes', 'feet']] = None  # default is feet
        self._in_with = False
    
    def at_only(self):
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

    def in_(self, dim: _Dimension):
        if isinstance(dim, str):
            self.dimension = Dimension(dim)
        else:
            self.dimension = dim
        return self

    def __call__(self, funct: Fun, at_only=False):
        """
        Call functions as/at this entity outside a with expression
        """
        # TODO: could dynamically decide if just as_ or just at are necessary
        subs = self._get_subs(pos_only=at_only)
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
        self._in_with = True
        return self

    # position and rotation
    def teleport(self, loc: Pos | PosRef | Rot | SingleEntity = Pos(), *rotation_args):
        if self._in_with:
            if self.execute_as_fun is not GLOBALS.fun:
                raise NotImplementedError("Cannot use entity outside of current scope")
            if isinstance(loc, PosRef):
                if self.execute_as_fun is loc.ref.execute_as_fun:
                    Teleport(_SelectorBase(), loc.pos, *rotation_args)
                else:
                    @fun
                    def f():
                        Teleport(_SelectorBase(), loc.pos, *rotation_args)
                    loc.ref(f, at_only=True)
                # else:
                #     raise NotImplementedError("Must specify at_parent")
            else:
                Teleport(_SelectorBase(), loc, *rotation_args)
        else:
            if isinstance(loc, PosRef):
                @fun
                def f():
                    Teleport(self, loc.pos, *rotation_args)
                loc.ref(f)
            else:
                Teleport(self, loc, *rotation_args)
    def propel(self, forward: int):
        Teleport(self, Pos.angular(forward=forward))
    @property
    def pos(self):
        return PosRef(pos=Pos(), ref=self)
    @pos.setter
    def pos(self, pos_: Pos | PosRef):
        self.teleport(pos_)
    @property
    def x(self):
        return _EntityRelative(self)
    @x.setter
    def x(self, x_):
        self.teleport(Pos(x=x_))
    @property
    def y(self):
        return _EntityRelative(self)
    @y.setter
    def y(self, y_):
        self.teleport(Pos(y=y_))
    @property
    def z(self):
        return _EntityRelative(self)
    @z.setter
    def z(self, z_):
        self.teleport(Pos(z=z_))
    @property
    def yaw(self):
        return _EntityRelative(self)
    @yaw.setter
    def yaw(self, yaw_):
        self.teleport(Rot(yaw=yaw_))
    @property
    def pitch(self):
        return _EntityRelative(self)
    @pitch.setter
    def pitch(self, pitch_):
        self.teleport(Rot(pitch=pitch_))

    def kill(self):
        if self._in_with and self.execute_as_fun is GLOBALS.fun:
            Kill(_SelectorBase())
        else:
            Kill(self)

    def _get_subs(self, pos_only=False):
        subs = []
        if pos_only:
            if self.as_selector is not None and self.at_target is not None and self.at_target != _SelectorBase():
                raise ValueError(f"Cannot cast {self.as_selector} and {self.at_target} to position")
            if self.as_selector == 'self':
                subs.append(ExecuteSub.at(self))
            elif self.as_selector:
                subs.append(ExecuteSub.at(self.as_selector))
            if isinstance(self.at_target, Pos):
                subs.append(ExecuteSub.positioned(self.at_target))
            elif isinstance(self.at_target, Rot):
                subs.append(ExecuteSub.rotated(self.at_target))
        else:
            if self.as_selector == 'self':
                subs.append(ExecuteSub.as_(self))
            elif self.as_selector:
                subs.append(ExecuteSub.as_(self.as_selector))
            if self.at_target:
                if isinstance(self.at_target, _SelectorBase):
                    subs.append(ExecuteSub.at(self.at_target))
                elif isinstance(self.at_target, Pos):
                    subs.append(ExecuteSub.positioned(self.at_target))
                elif isinstance(self.at_target, Rot):
                    subs.append(ExecuteSub.rotated(self.at_target))
        if self.dimension:
            subs.append(ExecuteSub.in_(self.dimension))
        if self.anchor:
            subs.append(ExecuteSub.anchored(self.anchor))
        if self.positioned:
            subs.append(ExecuteSub.positioned(self.positioned))
        if self.rotated:
            subs.append(ExecuteSub.rotated(self.rotated))
        if self.at_heightmap:
            subs.append(ExecuteSub.positioned(self.at_heightmap))
        return subs
    
    def __exit__(self, *args):
        self.execute_as_fun.__exit__()
        
        self(self.execute_as_fun)

class SingleEntity(Entities, _SingleSelectorBase):
    pass

class Players(Entities, _PlayerSelectorBase):
    pass

class SinglePlayer(Entities, _SinglePlayerSelectorBase):
    pass

class SelfEntity(SingleEntity):
    def __init__(self,
                 **selector_kwargs
                 ):
        super().__init__('s', **selector_kwargs)

class PosRef:
    def __init__(self, pos: Pos, ref: Entities):
        self.pos = pos
        self.ref = ref

class Summon(WithStatement):
    def __init__(self,    
                 entity_name: EntityType
                 ):
        self.entity_name = entity_name
        super().__init__('$summon', add=False)
        
    def __enter__(self):
        super().__enter__()
        return SelfEntity()
    
    def __call__(self, *statements: Statement):
        RawExecute([ExecuteSub.summon(self.entity_name)], list(statements))
