particle minecraft:dust{color:[1.0, 0.0, 0.0], scale:1.0} ~ ~1.5 ~ 0 0 0 0 1 force @a
scoreboard players remove @s i 1
execute as @s[scores={i=1..}] positioned ^ ^ ^1.4000000000000001 run function main:x0/x1/x1/x0/x0/x0/x0/x0