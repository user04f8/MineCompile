from math import cos, pi, sin

from langcraft import *
from langcraft.lib import *

CHAIN_TAG = '$invalid'

with Namespace('tracks'):
    init()

    @public
    def _debug():
        DebugStatement()


    @metafun()
    def perpendiculars(block_type, thickness: int):
        for i in range(-thickness, thickness+1):
            Statement(f'setblock ^{i} ^ ^ {block_type}')

    def next_chain():
        Statement(f'summon marker ^ ^ ^ {{Tags:[{CHAIN_TAG}]}}')
        Entities(tag=CHAIN_TAG).teleport(Pos(), Rot())

    @metafun()
    def turn_segment(radius, turn_degrees, block_type='ice', thickness=5, step_size=0.5, spiral_turn_degrees=0):
        # line(each_block=perpendiculars,
        #             continue_condition=Condition(True),
        #             max_len=100,
        #             step_dist=2)

        # degrees_per_step = (360 * step_size) / (2*pi * radius)
        turn_sgn = -1 if turn_degrees < 0 else 1
        turn_degrees = abs(turn_degrees)

        arc_length = 2 * pi * radius * (turn_degrees / 360)
        num_steps = round(arc_length / step_size)
        degrees_per_step = turn_degrees / num_steps

        with Fun() as f:
            perpendiculars(block_type, thickness)
            Statement('scoreboard players remove @s i 1')
            with Self(scores='{i=0}').at_parent():
                next_chain()
            if spiral_turn_degrees:
                with Self(scores=f'{{i={int(num_steps) // 2}..}}').at(Pos.angular(forward=step_size), rot=Rot(relative=True, yaw=turn_sgn*degrees_per_step + spiral_turn_degrees)):
                    f()
                with Self(scores=f'{{i=1..{int(num_steps) // 2 - 1}}}').at(Pos.angular(forward=step_size), rot=Rot(relative=True, yaw=turn_sgn*degrees_per_step)):
                    f()
            else:
                with Self(scores='{i=1..}').at(Pos.angular(forward=step_size), rot=Rot(relative=True, yaw=turn_sgn*degrees_per_step)):
                    f()
        Statement(f'scoreboard players set @s i {int(num_steps) + 1}')
        f()

    @metafun()
    def straight_segment(length, block_type='ice', thickness=5, step_size=0.5):
        num_steps = round(length / step_size)

        with Fun() as f:
            perpendiculars(block_type, thickness)
            Statement('scoreboard players remove @s i 1')
            with Self(scores='{i=0}').at_parent(): # TODO entity conditionals
                next_chain()
            with Self(scores='{i=1..}').at(Pos.angular(forward=step_size)):
                f()
        Statement(f'scoreboard players set @s i {int(num_steps) + 1}')
        f()

    @metafun()
    def lighting_decor():
        Statement('setblock ~ ~5 ~ glowstone')
        next_chain()

    def sequential(*segments, pass_args=(), schedule_offset=1) -> int:
        global CHAIN_TAG
        CHAIN_TAG = 'chain' #GLOBALS.gen_name('tag')
        # Statement(f'summon marker ~ ~ ~ {{Tags:["{CHAIN_TAG}"]}}')
        segment, *segments = segments
        segment(*pass_args)
        for i, segment in enumerate(segments):
            # @lambda_metafun
            # def nexttick():
            with Entities(tag=CHAIN_TAG):
                segment(*pass_args)
                Self().kill()
            # Statement(f'schedule {nexttick()} {i + schedule_offset}t')
        # @lambda_metafun
        # def finaltick():
        Entities(tag=CHAIN_TAG).kill()
        # Statement(f'schedule {finaltick()} {len(segments) + schedule_offset}t')
        return len(segments) + schedule_offset + 1

    @public
    def first_track():
        W, H = 40, 50
        ice_block = 'packed_ice'
        edge_block = 'grass_block'
        low_block = 'dirt'
        def track_base(block, thickness):
            sequential(
                lambda: straight_segment(H, block_type=block, thickness=thickness),
                lambda: turn_segment(W / 3, 90, block_type=block, thickness=thickness),
                lambda: straight_segment(W / 3, block_type=block, thickness=thickness),
                lambda: turn_segment(W / 3, 90, block_type=block, thickness=thickness),
                lambda: straight_segment(H, block_type=block, thickness=thickness),
                lambda: turn_segment(W / 2, 180, block_type=block, thickness=thickness)
            )
        with Self().at(Pos.relative(y=-1), rot=Rot(pitch=0)):
            track_base(edge_block, 6)
            track_base(ice_block, 5)
        with Self().at(Pos.relative(y=-2), rot=Rot(pitch=0)):
            track_base(edge_block, 7)
        with Self().at(Pos.relative(y=-3), rot=Rot(pitch=0)):
            track_base(low_block, 4)

    @public
    def the_circle():
        with Self().at(Pos.angular(left=50), rot=Rot(pitch=0)):
            turn_segment(50, 360, 'packed_ice', 7)
        with Self().at(Pos.angular(left=46), rot=Rot(pitch=0)):
            turn_segment(46, 360, 'blue_ice', 4)


    @public
    def double_double_cake():
        with Self().at(Pos.relative(y=50)):
            with Self().at(Pos.angular(left=20), rot=Rot(pitch=0)):
                turn_segment(20, 360, 'packed_ice', 5)
            with Self().at(Pos.angular(left=16), rot=Rot(pitch=0)):
                turn_segment(16, 360, 'blue_ice', 4)
        
        with Self().at(Pos.relative(y=30)):
            with Self().at(Pos.angular(left=30), rot=Rot(pitch=-3)):
                turn_segment(30, 360, 'blue_ice', 3)

        with Self().at(Pos.relative(y=10)):
            with Self().at(Pos.angular(left=40), rot=Rot(pitch=-1)):
                turn_segment(40, 360, 'packed_ice', 7)
        
        with Self().at(Pos.relative(y=-10)):
            Statement('fill ~-42 ~ ~-42 ~42 ~ ~42 white_concrete')
            with Self().at(Pos.angular(left=52), rot=Rot(pitch=0)):
                
                turn_segment(52, 360, 'white_concrete', 12)
                turn_segment(52, 360, 'packed_ice', 10)


    @public
    def triple_helix():
        R = 20
        DEG = 3600//4
        with Self().at(Pos.relative(y=-10)):
            with Self().at(Pos.angular(left=R), rot=Rot(pitch=-7)):
                turn_segment(R, DEG + 2*360//3, 'packed_ice', 3)
        with Self().at(Pos.relative(y=-5)):
            with Self().at(Pos.angular(left=R), rot=Rot(pitch=-7)):
                turn_segment(R, DEG + 360//3, 'blue_ice', 3)
        with Self().at(Pos.relative(y=0)):
            with Self().at(Pos.angular(left=R), rot=Rot(pitch=-7)):
                turn_segment(R, DEG, 'ice', 3)
        with Self().at(Pos.relative(y=0)):
            with Self().at(Pos.angular(left=10), rot=Rot(pitch=0)):
                turn_segment(10, 360, 'slime_block', 10)

    @public
    def skeleparty():
        n = 16
        r = 5
        for i in range(5*n):
            Statement(f'summon skeleton ~{r*cos(2*pi*i / n):.4f} ~{i} ~{r*sin(2*pi*i / n):.4f}')
        
        Statement(f'enchant @e[type=skeleton, distance=..{n*r*5}] punch 2')
        with Self().at(Pos.relative(y=-5)):
            triple_helix()

    @fun.ticking
    def tnt_laser():
        with Entities('a', selected_item=JSON(id="minecraft:stone")).at(pos=Pos.relative(y=1.8)) as players:
            Statement('summon wind_charge ^ ^ ^5')
            Pass()
            # line(
            #     lambda: Pass(),
            #     Condition('block ~ ~ ~ air'),
            #     16*5,
            #     lambda: Statement('summon tnt ~ ~ ~'),
            #     step_dist=1
            # )
            # Statement(r'summon bat ~ ~ ~ {NoAI:true}')

    @public
    def random_track():
        ice_block = 'packed_ice'
        lambdas = []
        for i in range(1000):
            if randint(1, 2) == 1:
                lambdas.append(lambda block, thickness: straight_segment(random.randint(15, 45), block_type=block, thickness=thickness))
            elif randint(1, 2) == 1:
                turn_base_size = random.randint(-36, 36) + random.randint(-36, 36)
                turn_sharpness = random.randint(3, 5)
                lambdas.append(lambda block, thickness: turn_segment(2 * turn_base_size, turn_sharpness * turn_base_size, block_type=block, thickness=thickness))
            else:
                lambdas.append(lambda *args: lighting_decor())

        def track_base(block, thickness, offset=1):
            sequential(
                *lambdas,
                pass_args=(block, thickness),
                schedule_offset=offset
            )
        # track_base(edge_block, 6)
        with Self().at(Pos.relative(y=-1), rot=Rot(pitch=0)):
            track_base(ice_block, 5)
        # with Self().at(Pos.relative(y=0), rot=Rot(pitch=0)):
        #     track_base('air', 3, offset=60)
        # with Self().at(Pos.relative(y=1), rot=Rot(pitch=0)):
        #     track_base('air', 3, offset=120)

out = compile_all(write=True, root_dir='../datapacks/track_elements')
# display_all()
# print('---')
display(out, regex=r'main:x1/x0')
# display(out, regex=r'main:x1')