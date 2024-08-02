from typing import Literal

type EffectType = Literal[
    'speed', 'slowness', 'haste', 'mining_fatigue', 'strength', 'instant_health', 
    'instant_damage', 'jump_boost', 'nausea', 'regeneration', 'resistance', 
    'fire_resistance', 'water_breathing', 'invisibility', 'blindness', 'night_vision', 
    'hunger', 'weakness', 'poison', 'wither', 'health_boost', 'absorption', 
    'saturation', 'glowing', 'levitation', 'luck', 'unluck', 'fatal_poison', 
    'slow_falling', 'conduit_power', 'dolphins_grace', 'bad_omen', 
    'hero_of_the_village', 'darkness', 'trial_omen', 'raid_omen', 'wind_charged', 
    'weaving', 'oozing', 'infested'
]