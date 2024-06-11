from function import *
# from test0 import f

with Fun() as x:
    with While('block ~ ~ ~ air'):
        Statement('say hi')
    

with TickingFun():
    x()

display_all()