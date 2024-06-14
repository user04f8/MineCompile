from langcraft import *

with TickingFun():
    with Entity(Selector('e', type='marker', tags=['laser'])) as beam:
        with Fun() as f:
            beam.teleport(Pos.angular(forward=1))
            with If('block ~ ~ ~ air'):
                Statement('summon tnt')
                beam.kill()
            f()
        f()
        # with While('block ~ ~ ~ air'):
            
        

with PublicFun('summon_beam') as summon_beam:
    with Entity(Selector()).at(Pos.relative(0, 1.8, 0)) as s:
        Statement('summon marker ^ ^ ^5 {Tags:["laser"]}')



display_all(max_optim_steps=5)
compile_all(write=True)