from langcraft import *

with PublicFun('move_chickens'):
    e = Entities(_SelectorType('e', type='chicken'))
    e.yaw += 15
    e.teleport(Pos.angular(forward=1))
    
with PublicFun('to_the_end'):
    with Entities(_SelectorType()).in_('the_end').at(Pos(0, 200, 0), on=Heightmap.surface) as s:
        Statement('say "I\'m going to the end!"')
        s.teleport()

    with Entities(_SelectorType()) as s:
        s.kill()

with Fun() as explode:
    Statement('summon ~ ~ ~ tnt')

with TickingFun():
    with Entities(_SelectorType('e', tags=['test'])) as players:
        players.x += 1
        players.y -= 0.1
        players.z -= 0.5
    with Entities(_SelectorType('e', tags=['propel'])) as propel:
        with While('block ~ ~ ~ air'):
            propel.teleport(Pos.angular(forward=1))
        explode()
        propel.kill()
    Entities(_SelectorType('e', tags=['explode']))(explode)
    

display_all()