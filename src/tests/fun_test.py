from langcraft import *
from langcraft.lib import *

with Namespace('fun_test'):
    init()
    
    @fun
    def tnt_line():
        with Self().at(Pos.angular(forward=8)):
            line(
                lambda: Statement('summon tnt ~ ~1.8 ~'),
                Condition(True),
                50
            )
            Kill(Self())


    @metafun()
    def guide_line(step_dist_mult):
        with Summon('marker'):
            with Self().at(Pos.angular(forward=1, left=-.3)):
                line(
                    lambda: (
                        Statement(r'particle minecraft:dust{color:[1.0, 0.0, 0.0], scale:1.0} ~ ~1.5 ~ 0 0 0 0 1 force @a'),
                        # Statement('summon pig ~ ~ ~'),
                        # Statement(f'say here')
                    ),
                    Condition(True),
                    16,
                    step_dist=.2 * step_dist_mult
                )
                
                Kill(Self())

    @public
    def tnt_laser():
        with Summon('marker'):
            tnt_line()

    @fun.ticking
    def tick():
        with Entities(tag='laser_cannon'):
            Statement(f'scoreboard players add @s charge 1')
            with Self(scores=dict(charge='170..')):
                @lambda_metafun
                def f():
                    with Self().at(Pos.angular(forward=8)):
                        Statement('tp @s ~ ~ ~ ~ ~')
                        Statement('tag @s add laser_cannon_sub')
                Statement(f'execute summon marker run {f()}')
                for i in range(15):
                    Statement(f'particle crit ^ ^ ^{i} 0 0 0 1 3')
                Statement('scoreboard players reset @s charge')
        
        with Entities(tag='laser_cannon_sub') as e:
            Statement(f'scoreboard players add @s charge 1')
            with Self(scores=dict(charge='..5')):
                guide_line(6)
            with Self(scores='{charge=6..9}'):
                guide_line(7)
            with Self(scores='{charge=10..13}'):
                guide_line(8)
            with Self(scores='{charge=14..}'):
                tnt_laser()
                e.kill()

    @fun.ticking
    def tick_():
        blocks = {'ice', 'packed_ice', 'blue_ice', 'glass', 'grass_block', 'bamboo_planks'}

        for block in blocks:
            with Entities('a', nbt=f'{{SelectedItem:{{id: "minecraft:{block}"}}}}'):
                for size in range(1, 9):
                    Statement(f'execute as @s[nbt={{SelectedItem:{{count: {size}}}}}] at @s on vehicle run fill ~-{(size+1)//2} ~ ~-{size//2} ~{(size+1)//2} ~ ~{size//2} {block}')
                    Statement(f'execute as @s[nbt={{SelectedItem:{{count: {size}}}}}] at @s on vehicle run fill ~-{size//2} ~ ~-{(size+1)//2} ~{size//2} ~ ~{(size+1)//2} {block}')
        
        for block in blocks:
            with Entities('a', nbt=f'{{Inventory:[{{Slot: -106b, id: "minecraft:{block}"}}]}}'):
                for size in range(1, 9):
                    Statement(f'execute as @s[nbt={{Inventory:[{{Slot: -106b, count: {size}}}]}}] at @s on vehicle run fill ~-{(size+2)//2} ~ ~-{size//2} ~{(size+2)//2} ~ ~{size//2} {block} replace air')
                    Statement(f'execute as @s[nbt={{Inventory:[{{Slot: -106b, count: {size}}}]}}] at @s on vehicle run fill ~-{size//2} ~ ~-{(size+2)//2} ~{size//2} ~ ~{(size+2)//2} {block} replace air')
                

        # with Entities('a') as a:
        #     Pass()
            # Statement('fill ~-3 ~-1 ~-3 ~3 ~-1 ~3 blue_ice')
            # Statement('fill ~-4 ~-1 ~-4 ~4 ~-1 ~4 ice replace air')
            # Statement('fill ~-3 ~1 ~-3 ~3 ~3 ~3 air')
    # Teleport(Entities('n', type='!player', distance='..4'), Pos.angular(forward=2))

    with Namespace('summon'):
        @public
        def plus_x_bounce():
            Pass()  # TODO


            
    with Namespace('checkpoint'):
        class Checkpoint:
            ANIMATION_T = GLOBALS.gen_name('scoreboard')
            ANIMATION_MAX = GLOBALS.gen_name('scoreboard')

            def __init__(self):
                
                self.tag = GLOBALS.gen_name('entity_tag')

                @fun.ticking
                def tick():
                    with Entities(tag=self.tag) as e:
                        Statement(f'scoreboard players add @s {self.ANIMATION_T} 1')
                        with ScoreTree(self.ANIMATION_T, cmds_per_score=2):
                            for i in range(1, 180):
                                Statement(f'say {i}')
                                Pass()
                            Statement('say 180')
                            Statement(f'scoreboard players set @s {self.ANIMATION_T} 0')
                
                @public
                def create_checkpoint():
                    Statement(f'execute summon marker run {self._create_sub()}')


            @lambda_metafun
            def _create_sub(self):
                Statement(f'scoreboard players set @s {self.ANIMATION_T} 180')

        Checkpoint()


    @fun.on_load
    def load():
        Statement(f'scoreboard objectives add i dummy')
        Statement(f'scoreboard objectives add charge dummy')
        Statement(f'scoreboard objectives add {Checkpoint.ANIMATION_T} dummy')
        Statement(f'scoreboard objectives add {Checkpoint.ANIMATION_MAX} dummy')
        DebugStatement(f'load complete')

    @fun.ticking
    def speedglass():
        with Entities('a'):
            with If('block ~ ~-1 ~ glass'):
                Statement('''
    effect give @s minecraft:speed 1 30 true
                ''')
            # with If('block ~ ~-1 ~ iron_block'):
            #     Statement('''
            #     attribute @s minecraft:generic.gravity modifier remove quick_track
            #     effect clear @s
            #     ''')

    @fun.ticking
    def terracotta():
        with Entities('a') as players:
            grav = Flag('grav')
            # Statement(ResetFlagToken(grav))
            with If('block ~ ~-3 ~ minecraft:gray_glazed_terracotta'):
                Statement(SetFlagToken(grav))
                DebugStatement('here')
                # Statement('ride @s dismount')
                Statement('execute align y run tp @s ~ ~-1 ~')
                Statement('execute as @n[type=boat, distance=..2] at @s align y run tp @s ~ ~-1 ~')
                Statement('ride @s mount @n[type=boat, distance=..5]')
                

            # with If(~Condition(str(CheckFlagToken(grav)))):
            #     Statement('say there')
            #     Statement('attribute @s minecraft:generic.gravity modifier remove terracotta')
            # with If('block ~ ~-1 ~ iron_block'):
            #     Statement('''
            #     attribute @s minecraft:generic.gravity modifier remove quick_track
            #     effect clear @s
            #     ''')

out = compile_all(write=True)
display(out, regex='ice')
display(out, regex='x3/xc')

# display(out, 'main:x2/x0', include_subs=False)


