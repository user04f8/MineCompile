from langcraft import *

@ticking
@fun
def tick():
    with Entity('n', tag='location') as s:
        with Entities(tag='goto') as e:
            e.teleport(s)

            Statement('say hi')

        Debug()

@public
def slow():
    with Entities(type='pig') as e:
        e.teleport(Pos.relative(y=3))

    mc.Effect.give(Entities(distance=5), '')


display_all()