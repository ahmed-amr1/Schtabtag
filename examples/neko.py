from anekos import NekosLifeClient, SFWImageTags
import discord
from discord.ext import commands

neko = NekosLifeClient()
client = commands.Bot(command_prefix=".")

"""
<'solog', 'smug', 'feet', 'smallboobs', 'lewdkemo', 'woof', 'gasm', 'solo', '8ball', 'goose', 'cuddle', 'avatar', 'cum', 'slap', 'les', 'v3', 'erokemo', 'bj', 'pwankg', 'nekoapi_v3.1', 'ero', 'hololewd', 'pat', 'gecg', 'holo', 'poke', 'feed', 'fox_girl', 'tits', 'nsfw_neko_gif', 'eroyuri', 'holoero', 'pussy', 'Random_hentai_gif', 'lizard', 'yuri', 'keta', 'neko', 'hentai', 'feetg', 'eron', 'erok', 'baka', 'kemonomimi', 'hug', 'cum_jpg', 'nsfw_avatar', 'erofeet', 'meow', 'kiss', 'wallpaper', 'tickle', 'blowjob', 'spank', 'kuni', 'classic', 'waifu', 'femdom', 'boobs', 'trap', 'lewd', 'pussy_jpg', 'anal', 'futanari', 'ngif', 'lewdk'>"
"""

@client.command()
async def nekos(ctx):
    result = await neko.image(SFWImageTags.CUDDLE)
    await ctx.send(result.url)

client.run('token')
