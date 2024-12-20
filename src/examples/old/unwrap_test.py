# py -m tests.unwrap_test

from langcraft import *

with Fun() as g:
    with Entities('e', tags='propel') as e:
        e.teleport(Pos.angular(forward=1))
        # e.x += 1

with Fun() as h:
    with If(Condition('block ~ ~ ~ air')):
        Statement('say bye')

with PublicFun('run_f'):
    # RawExecute([Condition('A')], run_statements=[FunStatement(g, attach_local_refs=True)])
    with If(Condition('B')):
        g()
    g()
    Teleport(Pos(1, 0, 0,))
    Teleport(Pos.relative(0, 1, 0))
    h()
    for i in range(10):
        Teleport(Pos.relative(10, 0, 0))

# display_all(max_optim_steps=0)
display_all(optim=1)
# display_all()