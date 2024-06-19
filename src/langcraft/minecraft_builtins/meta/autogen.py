data = """
EntitySprite boats.png: Sprite image for boats in Minecraft Boat 	boat
EntitySprite boat-with-chest.png: Sprite image for boat-with-chest in Minecraft Boat with Chest 	chest_boat
EntitySprite minecart-with-chest.png: Sprite image for minecart-with-chest in Minecraft Minecart with Chest 	chest_minecart
EntitySprite minecart-with-command-block.png: Sprite image for minecart-with-command-block in Minecraft Minecart with Command Block 	command_block_minecart
EntitySprite minecart-with-furnace.png: Sprite image for minecart-with-furnace in Minecraft Minecart with Furnace 	furnace_minecart
EntitySprite minecart-with-hopper.png: Sprite image for minecart-with-hopper in Minecraft Minecart with Hopper 	hopper_minecart
EntitySprite minecart.png: Sprite image for minecart in Minecraft Minecart 	minecart
EntitySprite minecart-with-monster-spawner.png: Sprite image for minecart-with-monster-spawner in Minecraft Minecart with Monster Spawner 	spawner_minecart
EntitySprite minecart-with-tnt.png: Sprite image for minecart-with-tnt in Minecraft Minecart with TNT 	tnt_minecart
"""


lines = data.strip().split('\n')

result = []

for line in lines:
    parts = line.split()
    last_word = parts[-1]
    result.append(last_word)

print(result)