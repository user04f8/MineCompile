# py -m tests.unwrap_test2

from langcraft import *

# with Fun() as hidden:
#     Statement('  f$')

# with Fun() as f:
#     Statement('$f')
#     # hidden()

# with Fun() as g:
#     f()
#     Statement('  $f')

# with Fun() as h:
#     g()
#     g()

# f()

with Fun() as say_hi:
    Statement('say hi')

with PublicFun('run_f'):
    # for _ in range(5):
    #     g()
    # g()
    

    with If('$condition'):
        say_hi()
        # Statement('say bye')
    # f()

display_all(optim=0)
# display_all()