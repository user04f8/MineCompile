scoreboard players add @s charge 1
execute as @s[scores={charge=..5}] at @s run function main:x0/x1/x0
execute as @s[scores={charge=6..9}] at @s run function main:x0/x1/x1
execute as @s[scores={charge=10..13}] at @s run function main:x0/x1/x2
execute as @s[scores={charge=14..}] at @s run function main:x0/x1/x3