import os

# URLs
DDRAGON_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
DDRAGON_CHAMPIONS_URL = "https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion.json"
DDRAGON_CHAMPION_DETAILS_URL = "https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion/{champion_name}.json"
DDRAGON_IMG_URL = "https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_name}.png"

PATCH_NOTES_BASE_URL = "https://www.leagueoflegends.com/pt-br/news/game-updates/patch-{version_slug}-notes/"

# Embed Colors
COLOR_BUFF = 0x2ECC71  # Green
COLOR_NERF = 0xE74C3C  # Red
COLOR_ADJUST = 0x3498DB  # Blue
COLOR_DEFAULT = 0x95A5A6 # Grey

# Emojis (Discord native or custom IDs)
EMOJI_BUFF = "🟩"
EMOJI_NERF = "🟥"
EMOJI_ADJUST = "🟦"
EMOJI_CHAMPION = "👤"

# Limits
MAX_EMBED_FIELDS = 25
MAX_DESCRIPTION_LENGTH = 4096
