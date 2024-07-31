from langcraft import *

@ticking
@fun
def tick():
    with SingleEntity('n', tag='location') as s:
        with Entities(tag='goto') as e:
            e.teleport(s)

            Statement('say hi')

        Debug()

@public
def slow():
    Effect.give(SelfEntity(), 'slowness', 6)


display_all(optim=False)