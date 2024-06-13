from langcraft import *

with PublicFun('move_chickens'):
    e = Entity(Selector('e', type='chicken'))
    e.yaw += 15
    e.teleport(Pos.angular(forward=1))
    
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