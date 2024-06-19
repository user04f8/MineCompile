from langcraft import *

__all__ = ('line',)

@metafun()
def line(each_block: Callable, continue_condition, max_len: int, final_block: Callable = lambda: None, step_dist = 1.):
    with Fun() as f:
        each_block()
        Statement('scoreboard players remove @s i 1')
        with Self(scores='{i=1..}').at(Pos.angular(forward=step_dist)):
            with If(continue_condition):
                f()
            with If(~continue_condition):
                final_block()
    
    Statement(f'scoreboard players set @s i {max_len}')
    f()
