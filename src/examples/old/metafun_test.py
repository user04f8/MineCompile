from langcraft import *

def say(x):
    Statement(f'say {x}')

@public('asdfjkl')
@fun
def f():
    Statement('say asdjfkljfds')

@fun.on_load
def onload():
    
    RawExecute([ExecuteSub.as_(SelfEntity())], [say('hi')])
    say('hi')
    say('bye')

display_all()
