from langcraft import *


e = Entity(Selector('e', type='chicken'))

with TickingFun():
    e.x += .1
    Entity(Selector('n')).yaw += 15
    with Entity(Selector('a')) as players:
        players.x += 1
        players.y = 0
        players.z = 0 


display_all()