from math import pi

from langcraft import *
from langcraft.lib import *


@public
def _debug():
    DebugStatement()


@caching_metafun()
def perpendiculars(block_type, thickness: int):
    for i in range(-thickness, thickness+1):
        Statement(f'setblock ^{i} ^ ^ {block_type}')

@metafun
def turn_segment(radius, turn_degrees, block_type='ice', thickness=5, step_size=0.4):
    with Self().at(rot=Rot(pitch=0)):
        # line(each_block=perpendiculars,
        #             continue_condition=Condition(True),
        #             max_len=100,
        #             step_dist=2)

        # degrees_per_step = (360 * step_size) / (2*pi * radius)

        arc_length = 2 * pi * radius * (turn_degrees / 360)
        num_steps = round(arc_length / step_size)
        degrees_per_step = turn_degrees / num_steps

        with Fun() as f:
            perpendiculars(block_type, thickness)
            Statement('scoreboard players remove @s i 1')
            with Self(scores='{i=1..}').at(Pos.angular(forward=step_size), rot=Rot(relative=True, yaw=degrees_per_step)):
                f()
        Statement(f'scoreboard players set @s i {int(num_steps) + 1}')
        f()

@metafun
def segment(length, block_type='ice', thickness=5, step_size=0.5):
    with Self().at(rot=Rot(pitch=0)):
        num_steps = round(length / step_size)

        with Fun() as f:
            perpendiculars(block_type, thickness)
            Statement('scoreboard players remove @s i 1')
            with Self(scores='{i=1..}').at(Pos.angular(forward=step_size)):
                f()
            with Self(scores='{i=0}'):
                Statement('tp @s ~ ~ ~ ~ ~')
        Statement(f'scoreboard players set @s i {int(num_steps) + 1}')
        f()
            

@public
def _test():
    segment(50)
    turn_segment(15, 90)
    segment(15)

out = compile_all(write=True, root_dir='../datapacks/track_elements')
display_all()
