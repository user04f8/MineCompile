from function import *

with Pathspace('test'):
    Statement('say hi')
    Statement('say bye')

Fun[int] ('return4') (
    Statement('do stuff to set val to 4 and return')
)

display_all()