from math import cos, pi, sin

from langcraft import *
from .utils import test
test = test(__name__)

@test
def test0():
    @public
    def main():
        with ScoreTree('i', cmds_per_score=2, leafs_terminal=True):
            for i in range(16):
                Statement(f'say {i}')
                Kill()

@test
def test1():
    @ticking
    def main():
        with Entities(tag='spiral_anchor'):
            def f(t: int) -> tuple[float, float, float]:
                return .8 * t, 3*cos(t * pi/180), 3*sin(t * pi/180)
            
            with SingleEntity('n', tag='spiral').at_parent() as e:
                with ScoreTree('t'):
                    for t in range(4):
                        x, y, z = f(t)
                        e.teleport(Pos.relative(x, y, z))
