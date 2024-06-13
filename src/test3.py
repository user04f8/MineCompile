from langcraft import *

with PublicFun('move_chickens'):
    e = Entity(Selector('e', type='chicken'))
    e.yaw += 15
    e.teleport(Pos.angular(forward=1))
    
with PublicFun('to_the_end'):
    with Entity(Selector()).in_('the_end').at(pos=Pos(0, 200, 0), on=Heightmap.surface) as s:
        Statement('say "I\'m going to the end!"')
        s.teleport()

    with Entity(Selector()) as s:
        s.kill()

with Fun() as explode:
    Statement('summon ~ ~ ~ tnt')

with TickingFun():
    with Entity(Selector('e', tags=['test'])) as players:
        players.x += 1
        players.y -= 0.1
        players.z -= 0.5
    with Entity(Selector('e', tags=['propel'])) as propel:
        with While('block ~ ~ ~ air'):
            propel.teleport(Pos.angular(forward=1))
        explode()
        propel.kill()
    Entity(Selector('e', tags=['explode']))(explode)
    

display_all()