from typing import Optional

from .base import Fun, Statement, Block
from .types import Selector, Pos, Rot, _Relative, SingleSelector
from .commands import Teleport, RawExecute, ExecuteSub

class _EntityRelative(_Relative):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity

class Entity:
    def __init__(self, selector: Selector):
        self.selector = selector

    # position and rotation
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
    
    def __enter__(self):
        self.execute_as_fun = Fun().__enter__()
        self.old_selector = self.selector
        self.selector = SingleSelector()
        return self
        
    def __exit__(self, *args):
        self.execute_as_fun.__exit__()
        self.selector = self.old_selector
        Statement(RawExecute.as_cmds([ExecuteSub.as_(self.selector)], Block(self.execute_as_fun())))