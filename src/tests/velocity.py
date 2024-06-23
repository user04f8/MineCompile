from langcraft import *

Namespace('velocity').__enter__()

# def store_vel():
#     Statement('execute store result storage _internal:set_velocity x double 0.0001 run data get entity @s Motion[0] 10000')
#     Statement('execute store result storage _internal:set_velocity y double 0.0001 run data get entity @s Motion[1] 10000')
#     Statement('execute store result storage _internal:set_velocity z double 0.0001 run data get entity @s Motion[2] 10000')

# def write_vel():
#     # does not support players
#     for i, x in enumerate(('x', 'y', 'z')):
#         Statement(f'data modify entity @s Motion[{i}] set from storage _internal:set_velocity {x}')


@public
def summon_fireball():
    Statement(r'summon minecraft:small_fireball ^ ^ ^3 {Tags:["set_velocity"]}')
    Statement('execute store result score @s x run data get entity @s Pos[0]')
    for i, x in enumerate(('x', 'y', 'z')):
        Statement(f'execute store result score @s {x} run data get entity @s Pos[{i}]')
        Statement(f'execute store result score @n[tag=set_velocity] {x} run data get entity @n[tag=set_velocity] Pos[{i}]')
    for x in ('x', 'y', 'z'):
        Statement(f'scoreboard players operation @n[tag=set_velocity] {x} -= @s {x}')
    for x in ('x', 'y', 'z'):
        Statement(f'execute store result storage _internal:set_velocity {x} double 0.0001 run scoreboard players get @n[tag=set_velocity] {x}')
    for i, x in enumerate(('x', 'y', 'z')):
        Statement(f'data modify entity @s Motion[{i}] set from storage _internal:set_velocity {x}')
    Statement(f'tag @n[tag=set_velocity] remove set_velocity')

# TODO scoreboard objectives add x dummy

compile_all(write=True, root_dir='../datapacks/velocity')
