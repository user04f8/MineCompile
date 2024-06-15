from langcraft import *

def laser(each_tick: Fun, continue_condition: Condition, end_fun: Fun):
    with Fun() as f:
        each_tick()
        with Self().at(Pos.angular(forward=1)) as beam_forward:
            If(continue_condition)(
                f()
            ).Else(
                end_fun()
            )
    f()

with Fun() as f:
    Teleport(Pos.angular(forward=1))
    Statement('tag @s add laser')

with PublicFun('summon_beam'):
    with Self().at(Pos.relative(0, 1.8, 0)) as s:
        Statement([RawToken('execute summon marker run'), FunStatement(f, attach_local_refs=True).cmds[0].tokens[0]])

with Fun() as f:
    Teleport(Self(), Pos.angular(0, 0, 1), Rot())
    Statement('tag @s add explosion_trail')

with PublicFun('summon_explosion_beam') as seb:
    with Self().at(Pos.relative(0, 1.8, 0)) as s:
        Statement([RawToken('execute summon marker run'), FunStatement(f, attach_local_refs=True).cmds[0].tokens[0]])

with PublicFun('timed_explode') as timed_explode:
    with Entities(tag='timed_explosion') as e:
        Statement('summon tnt')
        e.kill()


with TickingFun():
    with Entities('e', tag='laser') as beam:
        # with While('block ~ ~ ~ air'):
        #     beam.teleport(Pos.angular(forward=1))
        with Fun() as each_tick:
            pass
        with Fun() as end_fun:
            Statement('setblock ~ ~ ~ glass')
            beam.kill()
        laser(each_tick, Condition('block ~ ~ ~ air'), end_fun)
    with Entities(tag='explosion_trail') as explosion_trail:
        explosion_trail.propel(1)

        Statement('scoreboard players add @s i 1')

        with Entities(scores='{i=6..100}') as explosion_trail:
            Statement('particle crit ~ ~ ~ 0 0 0 .3 10')
            Statement('summon marker ~ ~ ~ {Tags:["timed_explosion"]}')

        with Entities(scores='{i=100..}') as explosion_trail:
            timed_explode()
            explosion_trail.kill()
        # Statement('schedule function main:timed_exlpode 3s append')
    
    with Entities('e', tag='timed_explosion'):
        Statement('particle large_smoke ~ ~ ~ 0 0 0 .1 3')

with PublicFun('clock') as clock:
    # with Entity(Selector('e', type='vindicator')) as z:
    #     seb()
    Statement('schedule function main:clock 1s')

@fun
def say(x):
    Statement(f'say {x}')

with OnLoadFun():
    say('hi')
    Statement('scoreboard objectives add i dummy')
    Statement('schedule function main:clock 1s')


# compile_all(write=True, root_dir='../datapacks/compile_test/data')
display_all(max_optim_steps=0)
