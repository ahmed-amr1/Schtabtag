import time
import asyncio
import asyncpraw
import nextcord
import os
import psutil
import imports.language_check as language_check
import imports.yt as yt_module
import imports.binary as binary_module
import wikipedia as wiki_module
import translators as ts
import datetime
import platform
import random
import urllib.request
import urllib.parse
import re
import math
import orjson
import contextlib

from easy_pil.utils import load_image_async
from nextcord import Interaction, SlashOption
from nextcord.components import SelectOption
from nextcord.ui.select import Select
from textwrap import wrap
from anekos import NekosLifeClient, SFWImageTags
from nextcord.ext import commands, tasks, menus
from nextcord.ui import button, View, Button
from nextcord.interactions import Interaction
from pymongo import MongoClient
from easy_pil import Editor, Canvas, Font
from fractions import Fraction
from io import BytesIO
from typing import Union, Optional, List
from petpetgif import petpet as petpetgif
from itertools import cycle

begin = time.time()


def cos(x):
  return round(math.cos(math.radians(x)), 2)


def sin(x):
  return round(math.sin(math.radians(x)), 2)


def tan(x):
  return round(math.tan(math.radians(x)), 2)


def cls():
  if platform.system() == "Linux" or platform.system() == "Darwin":
    os.system("clear")
  if platform.system() == "Windows":
    os.system("cls")


with open("config.json", "r") as config:
  data = orjson.loads(config.read())

  OWNER_ID = data["owner_id"]

  TOKEN = data["token"]

  OFFICIAL_GUILD_ID = data["official_guild_id"]

  MONGO = data["mongo"]

  REDDIT_CLIENT_ID = data["reddit_client_id"]

  REDDIT_CLIENT_SECRET = data["reddit_client_secret"]

  PREFIX = data["prefix"]

CUSTOM_COLOR = 0xAC27FA

intents = nextcord.Intents.all()

cluster = MongoClient(MONGO)

bot = commands.Bot(
  command_prefix=commands.when_mentioned_or(PREFIX),
  intents=intents,
  help_command=None,
)

levelling = cluster["discord"]["levelling"]

statuses = cycle(
  [
    "with {member_count} members",
    "in {server_count} servers",
    ".help",
    "with Ahmed Amr#5544",
  ]
)


@tasks.loop(seconds=12)
async def change_status():
  await bot.wait_until_ready()
  status = next(statuses)
  if status.startswith("with ") and status.endswith("members"):
    status = status.format(member_count=len(bot.users))
  if status.startswith("in ") and status.endswith("servers"):
    status = status.format(server_count=len(bot.guilds))
  await bot.change_presence(
    status=nextcord.Status.idle, activity=nextcord.Game(status)
  )


@tasks.loop(seconds=1)
async def termination():
  files = os.listdir()
  for i in files:
    if i == "STOP_SIGN":
      os.remove("STOP_SIGN")
      await bot.close()
      print("FINISH")


@bot.event
async def on_ready():
  response = time.time() - begin

  sentence = f'{bot.user} is ready!\nTook {"{:.2f}".format(response)} secs to start.\nLatency : {round(bot.latency * 1000)}ms.'

  width = len(f"{bot.user} is ready!")

  print("+-" + "-" * width + "-+")

  for line in wrap(sentence, width):
    print("| {0:^{1}} |".format(line, width))

  print("+-" + "-" * (width) + "-+")

  f = open("READY", "w")
  f.close()
  channel = bot.get_channel(916091369787899924)
  em = nextcord.Embed(
    title="Schtabtag has just started!",
    description=f"You can now interact freely with {bot.user.mention}!",
    timestamp=datetime.datetime.utcnow(),
    color=CUSTOM_COLOR,
  )
  em.timestamp = datetime.datetime.utcnow()
  em.set_thumbnail(url=bot.user.display_avatar.url)
  await channel.send(embed=em)
  if not change_status.is_running():
    change_status.start()
  if not termination.is_running():
    termination.start()


class view(View):
  def __init__(self):
    super().__init__(timeout=None)

  @button(label="0", custom_id="counter button", style=nextcord.ButtonStyle.primary)
  async def counter(self, button: Button, interaction: Interaction):
    label = int(button.label)
    label += 1

    button.label = str(label)

    await interaction.response.edit_message(view=self)


class selfrole(View):
  def __init__(self):
    super().__init__(timeout=None)

  @button(
    label="Announcements role",
    custom_id="ann button",
    style=nextcord.ButtonStyle.primary,
  )
  async def ann(self, button: Button, interaction: Interaction):
    role = interaction.guild.get_role(916100172000399481)
    if role in interaction.user.roles:
      await interaction.user.remove_roles(role)
      await interaction.response.send_message(
        f"The {role.mention} role has been removed from your roles",
        ephemeral=True,
      )
    else:
      await interaction.user.add_roles(role)
      await interaction.response.send_message(
        f"The {role.mention} role has been added to your roles", ephemeral=True
      )


@bot.command()
async def self_roles(ctx: commands.Context):
  if ctx.guild.id == OFFICIAL_GUILD_ID and ctx.channel.id == 908780161040805888:
    await ctx.send("Select your roles:", view=selfrole())
  elif ctx.guild.id == OFFICIAL_GUILD_ID and ctx.channel.id != 908780161040805888:
    channel = ctx.guild.get_channel(908780161040805888)
    await ctx.send(f"Please use this command in {channel.mention}")
  elif ctx.guild.id != OFFICIAL_GUILD_ID:
    await ctx.send("Sorry but this command is exclusive for Schtabtag's bot server")


@bot.command(
  help="Displays a clickable button that increases its value when clicking on it"
)
async def count(ctx: commands.Context):
  await ctx.send("Count", view=view())


@bot.command()
async def pet(
  ctx: commands.Context,
  obj: Optional[Union[nextcord.PartialEmoji, commands.MemberConverter]],
):
  if type(obj) == nextcord.PartialEmoji:
    image = await obj.read()
  elif type(obj) == nextcord.member.Member:
    image = await obj.display_avatar.with_format("png").read()
  else:
    await ctx.reply(
      "Please use a custom emoji or mention a member to petpet their avatar."
    )
    return

  source = BytesIO(image)
  dest = BytesIO()
  petpetgif.make(source, dest)
  dest.seek(0)
  global EM
  file = nextcord.File(dest, filename=f"{image[0]}-petpet.gif")
  if type(obj) == nextcord.member.Member and obj == ctx.author:
    EM = nextcord.Embed(
      title=f"{ctx.author.name} pats {obj.name}",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).set_image(url=f"attachment://{image[0]}-petpet.gif")
  if type(obj) == nextcord.member.Member:
    EM = nextcord.Embed(
      title=f"{ctx.author.name} pats {obj.name}",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).set_image(url=f"attachment://{image[0]}-petpet.gif")
  if type(obj) == nextcord.PartialEmoji:
    EM = nextcord.Embed(
      title=f"{ctx.author.name} pats {obj.name}",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).set_image(url=f"attachment://{image[0]}-petpet.gif")
  await ctx.send(embed=EM, file=file)


@bot.command(
  aliases=["latency"],
  help="Displays the amount of latency of the bot in milliseconds",
)
async def ping(ctx: commands.Context):
  await ctx.send(f"Pong! in {round(bot.latency * 1000)}ms.")


@bot.command(aliases=["wiki"], help="Searches for a specific argument in wikipedia")
async def wikipedia(
  ctx: commands.Context,
  amount_of_sentences_to_search_for: int = 3,
  *,
  search_query: str,
):
  wiki_module.set_lang("en")

  search = nextcord.Embed(
    title="Wikipedia",
    description="Searching...",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )

  msg = await ctx.send(embed=search)

  try:
    em = nextcord.Embed(
      title="Wikipedia",
      description=f"{wiki_module.summary(search_query,sentences=amount_of_sentences_to_search_for)}",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.set_thumbnail(
      url="https://media.discordapp.net/attachments/893417057541050368/913832653927616562/2244px-Wikipedia-logo-v2.svg.png"
    )
  except:
    em = nextcord.Embed(
      title="Wikipedia",
      description=f"Couldn't find any result of that.",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
  em.set_footer(
    text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
  )
  await msg.edit(embed=em)


@bot.command(aliases=["av", "pfp"], help="Sends the avatar of a specific member")
async def avatar(ctx: commands.Context, *, member: commands.MemberConverter = None):
  avatar = None
  username = None
  if member == None:
    avatar = ctx.author.display_avatar.replace(size=3000, static_format="png").url
    username = ctx.author.name
  else:
    avatar = member.display_avatar.replace(size=3000, static_format="png").url
    username = member.name
  em = nextcord.Embed(
    title=f"{username}'s avatar",
    timestamp=datetime.datetime.utcnow(),
    color=CUSTOM_COLOR,
    url=avatar,
  )
  em.set_image(url=avatar)
  em.set_footer(
    text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
  )
  await ctx.send(embed=em)


responds = [
  "It is certain.",
  "It is decidedly so.",
  "Without a doubt.",
  "Yes definitely.",
  "You may rely on it.",
  "As I see it, yes.",
  "Most likely.",
  "Outlook good.",
  "Yes.",
  "Signs point to yes.",
  "Reply hazy, try again.",
  "Ask again later.",
  "Better not tell you now.",
  "Cannot predict now.",
  "Concentrate and ask again.",
  "Don't count on it.",
  "My reply is no.",
  "My sources say no.",
  "Outlook not so good.",
  "Very doubtful.",
]


@bot.command(
  aliases=["8ball", "eightBall"],
  help="Replies to polar (yes/no) question with one of the standard 8ball responses from Wikipedia",
)
async def eightball(ctx: commands.Context, *, question: str = None):
  if question == None:
    await ctx.send("Please specify a question.")
  else:
    embed = (
      nextcord.Embed(
        title="8ball", timestamp=datetime.datetime.utcnow(), color=CUSTOM_COLOR
      )
      .set_footer(
        text=f"Requested by {ctx.author.name}",
        icon_url=ctx.author.display_avatar.url,
      )
      .add_field(name="Question", value=question, inline=False)
      .add_field(name="Answer", value=random.choice(responds))
    )
    await ctx.send(embed=embed)


@bot.command(
  aliases=["math", "maths", "calc"], help="Solves a given mathematical equation"
)
async def calculate(ctx: commands.Context, *, equation: str):
  try:
    dict = {
      "e": math.e,
      "pi": math.pi,
      "root": math.sqrt,
      "squareroot": math.sqrt,
      "sqrt": math.sqrt,
      "degrees": math.degrees,
      "radians": math.radians,
      "sin": sin,
      "cos": cos,
      "tan": tan,
      "asin": math.asin,
      "acos": math.acos,
      "atan": math.atan,
      "pow": math.pow,
      "power": math.pow,
      "fract": Fraction,
      "ratio": Fraction,
      "fraction": Fraction,
      "round": round,
    }
    problem = equation
    problem = problem.replace("^", "**")
    problem = problem.replace(":", "/")
    solve = str(eval(problem, dict))
    em = nextcord.Embed(
      title="Problem",
      description=f"```py\n{equation}\n```",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.add_field(name="Solve", value=f" ```py\n{solve}\n```")
  except Exception as e:
    print(e)
    em = nextcord.Embed(
      title="Calculator",
      description=f"Couldn't solve that.",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.add_field(name="Error", value=f"```py\n{e}\n```")
  em.set_footer(
    text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
  )
  await ctx.send(embed=em)


@bot.command(aliases=["echo"], help="Repeats a specific text")
async def say(ctx: commands.Context, *, text):
  await ctx.send(text)


class CustomEmojiButtonMenuPages(menus.ButtonMenuPages, inherit_buttons=False):
  def __init__(self, source, timeout=60):
    super().__init__(source, timeout=timeout)

    self.add_item(menus.MenuPaginationButton(emoji=self.FIRST_PAGE, label="First"))
    self.add_item(
      menus.MenuPaginationButton(emoji=self.PREVIOUS_PAGE, label="Prev")
    )
    self.add_item(menus.MenuPaginationButton(emoji=self.NEXT_PAGE, label="Next"))
    self.add_item(menus.MenuPaginationButton(emoji=self.LAST_PAGE, label="Last"))

    self.children = [
      self.children[1],
      self.children[2],
      self.children[0],
      self.children[3],
      self.children[4],
    ]

    self._disable_unavailable_buttons()

  @nextcord.ui.button(label="stop", emoji="⏹")
  async def on_stop(self, button, interaction):
    self.stop()


class MySource(menus.ListPageSource):
  def __init__(self, data):
    super().__init__(data, per_page=1)
    self.total = 0

  async def format_page(self, menu, entries):
    if menu.current_page == 0:
      self.total = len(entries) + 1
    offset = menu.current_page * self.per_page
    export = entries
    page = f"`{menu.current_page+1}/{self.get_max_pages()}`"
    em = (
      nextcord.Embed(
        title=export[0],
        description=f"`{page}`\n{export[1]}",
        color=0xFF0000,
        url=export[2],
      )
      .set_footer(
        text=f"By {export[3]} , Published at {export[4][:export[4].index('T')]}"
      )
      .set_image(url=export[5])
    )
    return em


@bot.command(aliases=["yt"])
async def youtube(ctx: commands.Context, *, search_query: str = None):
  if search_query == None:
    await ctx.send("Please provide a valid search query")
  else:
    msg = await ctx.send(
      embed=nextcord.Embed(
        title="Please wait...",
        description="Please wait until the search results are ready...",
        color=0xFF0000,
        timestamp=datetime.datetime.utcnow(),
      ).set_footer(
        text=f"Requested by {ctx.author.name}",
        icon_url=ctx.author.display_avatar.url,
      )
    )
    videos = yt_module.search(search_query)
    temp = []
    for each in videos:
      temp.append(
        [
          each["title"],
          each["description"],
          each["url"],
          each["channel"],
          each["date"],
          each["cover"],
        ]
      )
    pages = CustomEmojiButtonMenuPages(source=MySource(list(temp)))
    await pages.start(ctx)
    await msg.delete()


class inv(View):
  def __init__(self):
    super().__init__(timeout=None)
    url = "https://bit.ly/schtabtag"
    self.add_item(nextcord.ui.Button(label="Invite", url=url))


@bot.command(aliases=["inv"])
async def invite(ctx: commands.Context):
  em = nextcord.Embed(
    title="Invite Schtabtag",
    url="https://bit.ly/schtabtag",
    description="**`Invite Schtabtag to your Discord server and enjoy all the bot features!`**",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_thumbnail(url=bot.user.display_avatar.url)
  em.set_footer(
    text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
  )
  await ctx.send(embed=em, view=inv())


class Dropdown(Select):
  def __init__(self):
    SelectOptions = [
      SelectOption(label="Africa"),
      SelectOption(label="Europe"),
      SelectOption(label="Asia"),
      SelectOption(label="North America"),
      SelectOption(label="South America"),
      SelectOption(label="Australia"),
    ]
    super().__init__(
      placeholder="Select your continent",
      min_values=1,
      max_values=1,
      options=SelectOptions,
    )

  async def callback(self, interaction: nextcord.Interaction):
    result = self.values[0]

    africa = interaction.guild.get_role(941295071612006420)

    asia = interaction.guild.get_role(941295081980297258)

    north_america = interaction.guild.get_role(941295418694856724)

    south_america = interaction.guild.get_role(941295301128499221)

    europe = interaction.guild.get_role(941295411933634600)

    australia = interaction.guild.get_role(941296077326409819)

    roles = [africa, asia, north_america, south_america, europe, australia]

    if result == "Africa":
      if not africa in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(africa)
        return await interaction.response.send_message(
          "You are African now", ephemeral=True
        )
      if africa in interaction.user.roles:
        await interaction.user.remove_roles(africa)
        return await interaction.response.send_message(
          "You are not African now", ephemeral=True
        )

    if result == "Europe":
      if not europe in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(europe)
        return await interaction.response.send_message(
          "You are European now", ephemeral=True
        )
      if europe in interaction.user.roles:
        await interaction.user.remove_roles(europe)
        return await interaction.response.send_message(
          "You are not European now", ephemeral=True
        )

    if result == "Asia":
      if not asia in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(asia)
        return await interaction.response.send_message(
          "You are Asian now", ephemeral=True
        )
      if asia in interaction.user.roles:
        await interaction.user.remove_roles(asia)
        return await interaction.response.send_message(
          "You are not Asian now", ephemeral=True
        )

    if result == "North America":
      if not north_america in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(north_america)
        return await interaction.response.send_message(
          "You are North American now", ephemeral=True
        )
      if north_america in interaction.user.roles:
        await interaction.user.remove_roles(north_america)
        return await interaction.response.send_message(
          "You are not North American now", ephemeral=True
        )

    if result == "South America":
      if not south_america in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(south_america)
        return await interaction.response.send_message(
          "You are South American now", ephemeral=True
        )
      if south_america in interaction.user.roles:
        await interaction.user.remove_roles(south_america)
        return await interaction.response.send_message(
          "You are not South American now", ephemeral=True
        )

    if result == "Australia":
      if not australia in interaction.user.roles:
        for role in roles:
          try:
            await interaction.user.remove_roles(role)
          except:
            print(f"couldn't remove {role} from {interaction.user}")
        await interaction.user.add_roles(australia)
        return await interaction.response.send_message(
          "You are Australian now", ephemeral=True
        )
      if australia in interaction.user.roles:
        await interaction.user.remove_roles(australia)
        return await interaction.response.send_message(
          "You are not Australian now", ephemeral=True
        )


class DropdownView(View):
  def __init__(self):
    super().__init__()
    self.add_item(Dropdown())


@bot.command()
async def toBinary(ctx: commands.Context, *, argument):
  binary_list = binary_module.toBinary(argument)
  tmp = []
  for binary_item in binary_list:
    tmp.append(str(binary_item))
  result = " ".join(tmp)

  em = (
    nextcord.Embed(
      title="Text to binary code",
      timestamp=datetime.datetime.utcnow(),
      color=CUSTOM_COLOR,
    )
    .add_field(name="Text format", value=f"`{argument}`")
    .add_field(name="Binary format", value=f"```py\n{result}\n```")
    .set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
  )

  await ctx.send(embed=em)


@bot.command(aliases=["toString"])
async def toText(ctx: commands.Context, *, argument):
  binary_list = argument.split(" ")
  tmp = []
  for binary_item in binary_list:
    tmp.append(int(binary_item))
  result = binary_module.toString(tmp)

  em = (
    nextcord.Embed(
      title="Text to binary code",
      timestamp=datetime.datetime.utcnow(),
      color=CUSTOM_COLOR,
    )
    .add_field(name="Text format", value=f"```py\n'{result}'\n```")
    .add_field(name="Binary format", value=f"`{argument}`")
    .set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
  )

  await ctx.send(embed=em)


@bot.command(help="Bans a specific member from the current server")
@commands.has_permissions(ban_members=True)
async def ban(
  ctx: commands.Context, user: commands.MemberConverter, reason: str = None
):
  member = await bot.fetch_user(user.id)
  em = (
    nextcord.Embed(
      title="BAN", color=CUSTOM_COLOR, timestamp=datetime.datetime.utcnow()
    )
    .add_field(name=member, value=member.id)
    .add_field(name="REASON", value=reason)
    .set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    .set_thumbnail(url=member.display_avatar.url)
  )
  await ctx.send(embed=em)
  await ctx.guild.ban(user=user, reason=reason)


@bot.command(help="Kicks a specific member from the current server")
@commands.has_permissions(kick_members=True)
async def kick(
  ctx: commands.Context, user: commands.MemberConverter, reason: str = None
):
  member = await bot.fetch_user(user.id)
  em = (
    nextcord.Embed(
      title="KICK", color=CUSTOM_COLOR, timestamp=datetime.datetime.utcnow()
    )
    .add_field(name=member, value=member.id)
    .add_field(name="REASON", value=reason)
    .set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    .set_thumbnail(url=member.display_avatar.url)
  )
  await ctx.send(embed=em)
  await ctx.guild.kick(user=user, reason=reason)


@bot.command(hidden=True)
@commands.is_owner()
async def log(ctx: commands.Context, *, arg):
  print(arg)
  await ctx.message.delete()


@bot.command(hidden=True)
@commands.is_owner()
async def close(ctx: commands.Context):
  os.remove("READY")
  await ctx.message.delete()
  await bot.close()


@bot.command(hidden=True)
async def continent(ctx: commands.Context):
  view = DropdownView()
  if ctx.guild.id == OFFICIAL_GUILD_ID:
    if ctx.channel.name == "roles":
      await ctx.send("Choose your continent ", view=view)
    else:
      await ctx.send("This command is only available in <#908780161040805888>")
  else:
    await ctx.send("This command is only available in Schtabtag's official server")


@bot.command(
  aliases=["length", "len"], help="Measures a specific set of digits or characters"
)
async def measure(ctx: commands.Context, *, text_to_be_measured=None):
  if text_to_be_measured == None:
    await ctx.send("Please provide text to be measured")
  else:
    await ctx.reply(
      f"Text : `{text_to_be_measured}`\nThe number of characters in the text : `{len(text_to_be_measured)}`"
    )


@bot.command(
  aliases=["cl", "purge", "delete", "remove"],
  help="Deletes a specific number of messages in a channel",
)
@commands.has_permissions(manage_messages=True)
async def clear(ctx: commands.Context, amount_of_messages_to_be_deleted: int = 1):
  await ctx.channel.purge(limit=amount_of_messages_to_be_deleted + 1)


@clear.error
async def clear_error(ctx: commands.Context, error: commands.CommandError):

  if isinstance(error, commands.CommandOnCooldown):
    message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
  elif isinstance(error, commands.MissingPermissions):
    message = "You are missing the required permissions to run this command!"
  elif isinstance(error, commands.MissingRequiredArgument):
    message = f"Missing a required argument: {error.param}"
  elif isinstance(error, commands.ConversionError):
    message = str(error)
  else:
    message = "Oh no! Something went wrong while running the command!"

  await ctx.reply(message, delete_after=6)
  await ctx.message.delete(delay=6)


@wikipedia.error
async def wikipedia_error(ctx: commands.Context, error: commands.CommandError):

  if isinstance(error, commands.CommandOnCooldown):
    message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
  elif isinstance(error, commands.MissingPermissions):
    message = "You are missing the required permissions to run this command!"
  elif isinstance(error, commands.MissingRequiredArgument):
    message = f"Missing a required argument: {error.param}"
  elif isinstance(error, commands.ConversionError):
    message = str(error)
  else:
    message = "Oh no! Something went wrong while running the command!"

  await ctx.reply(message, delete_after=6)
  await ctx.message.delete(delay=6)


@bot.command(help="Converts given set of letters or numbers into emojis")
async def emojify(ctx: commands.Context, *, text_to_be_converted_to_emojis):
  if len(text_to_be_converted_to_emojis) < 120:
    real = text_to_be_converted_to_emojis.lower()
    alphabet = [
      "a",
      "b",
      "c",
      "d",
      "e",
      "f",
      "g",
      "h",
      "i",
      "j",
      "k",
      "l",
      "m",
      "n",
      "o",
      "p",
      "q",
      "r",
      "s",
      "t",
      "u",
      "v",
      "w",
      "x",
      "y",
      "z",
    ]
    numbers = {
      "1": "one",
      "2": "two",
      "3": "three",
      "4": "four",
      "5": "five",
      "6": "six",
      "7": "seven",
      "8": "eight",
      "9": "nine",
      "0": "zero",
      "*": "asterisk",
      "#": "hash",
    }

    result = ""
    for each in real:
      if each == " ":
        result += "    "
      if each in alphabet:
        result += f":regional_indicator_{each}:"
      if each in numbers:
        result += f":{numbers[each]}:"

    await ctx.send(result)
  else:
    await ctx.send("Please make your argument less than 120 characters")


@bot.command(help="Gives information about a given user")
async def userinfo(
  ctx: commands.Context,
  user_to_display_information_about: commands.MemberConverter = None,
):
  member = user_to_display_information_about
  if member == None:
    member = ctx.author
  member = (await ctx.guild.query_members(user_ids=[member.id], presences=True))[0]
  roles = [role.mention for role in member.roles[1:]]
  role = " ".join(roles)
  if len(roles) == 0:
    role = "No roles"
  date_format = "%a, %b %d, %Y %I:%M %p"
  av = member.display_avatar.url
  em = nextcord.Embed(
    title="User Info:",
    timestamp=datetime.datetime.utcnow(),
    description=f"{member.name}'s information:",
    colour=CUSTOM_COLOR,
  )
  em.add_field(name="ID", value=f"```py\n{member.id}```", inline=False)
  em.add_field(
    name="USERNAME",
    value=f"```\n{member.name}#{member.discriminator}```",
    inline=False,
  )
  em.add_field(
    name="JOINED SERVER ON",
    value=f"```\n{member.joined_at.strftime(date_format)}```",
    inline=False,
  )
  em.add_field(
    name="CREATED ACCOUNT ON",
    value=f"```\n{member.created_at.strftime(date_format)}```",
    inline=False,
  )
  em.add_field(name="ROLES", value=f"{role}", inline=False)
  em.add_field(
    name="STRONGEST ROLE", value=f"{member.top_role.mention}", inline=False
  )
  bot = "No"
  if member.bot:
    bot = "Yes"
  nick = "No nickname for this user"
  if member.nick != None:
    nick = member.nick
  em.add_field(name="BOT", value=f"```\n{bot}```", inline=False)
  status = "Can't access the status"
  if member.status is nextcord.Status.online:
    status = "Online"
  if member.status is nextcord.Status.offline:
    status = "Offline"
  if (
    member.status is nextcord.Status.dnd
    or member.status is nextcord.Status.do_not_disturb
  ):
    status = "Do not disturb"
  if member.status is nextcord.Status.idle:
    status = "Idle"
  if member.status is nextcord.Status.invisible:
    status = "Invisible"
  em.add_field(name="NICKNAME", value=f"```\n{nick}```", inline=False)
  em.add_field(name="CURRENT STATUS", value=f"```\n{member.status}```", inline=False)
  activity = "Nothing"
  if member.activity != None:
    activity = f"{member.activity.type.name} {member.activity.name} ({member.activity.details})"
  em.add_field(name="CURRENT ACTIVITY", value=f"```\n{activity}```", inline=False)
  em.set_footer(
    text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.display_avatar.url
  )
  em.set_thumbnail(url=av)
  await ctx.send(embed=em)


@bot.command(
  aliases=["hex"],
  help="Converts a Hexadecimal color code into a RGB color and previews it",
)
async def hexadecimal(ctx: commands.Context, hex_code=None):
  if hex_code == None:
    await ctx.send("Please specify a Hexadecimal color.")
  else:
    try:
      result = ""
      final = "#"
      if hex_code.startswith("#"):
        final += hex_code.replace("#", "")
      if hex_code.startswith("#") == False:
        final += hex_code
      red = "0x" + final[1] + final[2]
      green = "0x" + final[3] + final[4]
      blue = "0x" + final[5] + final[6]
      red = int(red, base=0)
      green = int(green, base=0)
      blue = int(blue, base=0)
      link = f"https://singlecolorimage.com/get/{final[1:]}/900x900.png"
      em = nextcord.Embed(
        title=f"({red},{green},{blue})",
        description=f"{final.upper()}",
        color=nextcord.Color.from_rgb(red, green, blue),
        timestamp=datetime.datetime.utcnow(),
      )
      em.set_image(url=link)
    except:
      em = nextcord.Embed(
        title=f"Error",
        description=f"Please provide a valid hexadecimal code like #7378F",
        color=0xFFFFFF,
        timestamp=datetime.datetime.utcnow(),
      )
    em.set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    await ctx.send(embed=em)


@bot.command(help="Converts a RGB color into Hexadecimal color code")
async def rgb(ctx: commands.Context, *, rgb_color=None):
  if rgb_color == None:
    await ctx.send("Please specify an RGB color.")
  else:
    try:
      result = ""
      show = ""
      if rgb_color.startswith("(") and rgb_color.endswith(")"):
        fin = rgb_color[1:-1].split(",")
        show = rgb_color[1:-1]
      if rgb_color.startswith("(") == False and rgb_color.endswith(")") == False:
        fin = rgb_color.split(",")
        show = rgb_color
      fin = [int(n.strip()) for n in fin]

      for each in fin:
        hexadecimal = hex(each)[2:]
        if len(hexadecimal) == 1:
          hexadecimal = "0" + hexadecimal
        result += hexadecimal
      link = f"https://singlecolorimage.com/get/{result}/900x900.png"
      em = nextcord.Embed(
        title=f"#{result.upper()}",
        description=f"({show})",
        color=nextcord.Color.from_rgb(fin[0], fin[1], fin[2]),
        timestamp=datetime.datetime.utcnow(),
      )
      em.set_image(url=link)
    except:
      em = nextcord.Embed(
        title=f"Error",
        description=f"Please provide a valid RGB color like (12,34,56)",
        color=0xFFFFFF,
        timestamp=datetime.datetime.utcnow(),
      )
    em.set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    await ctx.send(embed=em)


@bot.command(help="Converts a specific given text into uwu-text~")
async def uwu(ctx: commands.Context, *, text_to_be_converted_to_uwu_case):
  real = text_to_be_converted_to_uwu_case.lower()
  for each in real:
    real = real.replace("thing", "fing")
    real = real.replace("l", "w")
    real = real.replace("r", "w")
  await ctx.send(real + "~")


@bot.command(help="Displays the current channel and server which the user is in")
async def whereami(ctx: commands.Context):
  await ctx.send(f"You are in ({ctx.guild.name}) in {ctx.channel.mention} channel")


@bot.command(aliases=["stats"], help="Displays information about Schtabtag")
async def statistics(ctx: commands.Context):
  username = bot.user
  servers = len(bot.guilds)
  nextcordV = nextcord.__version__
  process = psutil.Process(os.getpid())
  ram = (process.memory_info().rss / 1000) / 1000
  ram = "{:.2f}".format(ram)
  ram = str(ram) + "mb"
  ver = platform.python_version()
  em = nextcord.Embed(
    title=f"Bot's statstics",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.add_field(
    name=":crown:OWNER'S ID:crown:", value=f"```py\n{OWNER_ID}```", inline=True
  )
  em.add_field(
    name="<:py:893420197132771378>PYTHON VERSION<:py:893420197132771378>",
    value=f"```py\n{ver}```",
    inline=True,
  )
  ping = bot.latency * 1000
  ping = round(ping)
  em.add_field(name=":zap:LATENCY:zap:", value=f'```py\n"{ping}ms"```', inline=True)
  em.add_field(name="FULL USERNAME", value=f"```py\n{username}```", inline=True)
  em.add_field(
    name=":school:SERVERS:school:", value=f"```py\n{servers}```", inline=True
  )
  em.add_field(
    name=":bar_chart:RAM USAGE:bar_chart:", value=f'```py\n"{ram}"```', inline=True
  )
  em.add_field(
    name="<:nextcord:901845590663643147>DISCORD VERSION<:nextcord:901845590663643147>",
    value=f"```py\n{nextcordV}```",
    inline=True,
  )
  em.add_field(
    name=":computer:HOST:computer:",
    value=f'```py\n"Being hosted on my owner\'s laptop."```',
    inline=False,
  )
  em.add_field(
    name=":timer:ELAPSED TIME:timer:",
    value=f"```py\n{int((time.time() - begin) / 60)} minutes\n```",
  )
  date_format = "%a, %b %d, %Y %I:%M %p"
  em.set_footer(
    text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.display_avatar.url
  )
  await ctx.send(embed=em)


@bot.command(help="Displays information about the current server")
async def serverinfo(ctx: commands.Context):
  date_format = "%a, %b %d, %Y %I:%M %p"
  server = ctx.guild
  name = server.name
  em = nextcord.Embed(
    title="Server info",
    description=f"Information about {name}",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  id = server.id
  description = server.description
  icon = server.icon.url
  if ctx.guild.banner != None:
    banner = server.banner.url
    em.set_image(url=banner)
  else:
    banner = None
  humans = len(server.humans)
  bots = len(server.bots)
  owner = server.owner
  created = server.created_at
  em.add_field(name="ID", value=f"```\n{id}```", inline=False)
  em.add_field(name="NAME", value=f"```\n{name}```", inline=False)
  em.add_field(
    name="CREATED ON",
    value=f"```\n{created.strftime(date_format)}```",
    inline=False,
  )
  em.add_field(name="HUMANS", value=f"```\n{humans}```", inline=False)
  em.add_field(name="DESCRIPTION", value=f"```\n{description}```", inline=False)
  em.add_field(name="BOTS", value=f"```\n{bots}```", inline=False)
  em.add_field(name="OWNER", value=f"```\n{owner}```", inline=False)
  em.set_thumbnail(url=icon)
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.command(
  aliases=["trans", "googletrans", "googletranslate"],
  help="Translates the passed argument into the passed language (Default:English)",
)
async def translate(ctx: commands.Context, From=None, To=None, *, question: str = None):
  try:
    src = From
    dst = To
    src = language_check.Check(src)
    dst = language_check.Check(dst)
    search = nextcord.Embed(
      title="Translating...",
      description='```py\n"Please wait..."```',
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    msg = await ctx.send(embed=search)
    em = nextcord.Embed(
      title="Translator",
      description=f"From ({src}) To ({dst})",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.add_field(name="Source text", value=f'```py\n"{question}"```', inline=False)
    em.add_field(
      inline=False,
      name="Translated text",
      value=f'```py\n"{ts.google(question,to_language=To,from_language=From)}"```',
    )
    em.set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    await msg.edit(embed=em)
  except:
    em = nextcord.Embed(
      description="Please check your arguments again.\nSyntax `trans src-lang dest-lang text`\nYou can read language abbreviations from [here](https://pastebin.com/PrxskfGq).",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.set_footer(
      text=f"Requested by {ctx.author.name}",
      icon_url=ctx.author.display_avatar.url,
    )
    await msg.edit(embed=em)


@bot.command(help="Reverses specific text which is given as an argument")
async def reverse(ctx: commands.Context, *, text: str):
  result = text[::-1]
  await ctx.send(result)


@bot.command()
async def roles(ctx: commands.Context, member: commands.MemberConverter = None):
  user = member
  if user == None:
    user = ctx.author
  if len(user.roles[1:]) >= 1:
    role = [role.mention for role in user.roles[1:]]
    em = nextcord.Embed(
      title=f"Roles for {user.name}",
      description="\n".join(role),
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.set_thumbnail(url=user.display_avatar.url)
    em.set_footer(
      icon_url=ctx.author.display_avatar.url,
      text=f"Requested by {ctx.author.name}",
    )
    await ctx.send(embed=em)
  else:
    role = ["No roles were found for this user."]
    await ctx.send(" ".join(role))


@bot.command()
async def count_commands(ctx: commands.Context):
  await ctx.send(
    f"There are {len(list(bot.all_commands.values()))} commands in Schtabtag including this command"
  )


@bot.command()
async def early_supporters(ctx: commands.Context):
  server = bot.get_guild(OFFICIAL_GUILD_ID)
  role = server.get_role(912018955340767253)
  supporters = []
  for member in server.members:
    if role in member.roles:
      supporters.append(str(member))
  em = nextcord.Embed(
    title="Early supporters",
    description="\n".join(supporters),
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


def age(birthdate):
  today = datetime.date.today()
  age = (
    today.year
    - birthdate.year
    - ((today.month, today.day) < (birthdate.month, birthdate.day))
  )
  return age


@bot.command()
async def owner(ctx: commands.Context):
  id = 819652262993461279
  server = bot.get_guild(OFFICIAL_GUILD_ID)
  member = server.get_member(id)
  em = nextcord.Embed(
    title="Owner",
    description=f"The owner of {bot.user.mention}",
    timestamp=datetime.datetime.utcnow(),
    color=CUSTOM_COLOR,
  )
  em.set_thumbnail(url=member.display_avatar.url)
  em.add_field(name="ID", value=f"{id}", inline=False)
  em.add_field(name="Full username", value=f"{member}", inline=False)
  em.add_field(name="Nationality", value=f"Egyptian", inline=False)
  em.add_field(name="Age", value=f"{age(datetime.date(2007,3,11))}", inline=False)
  em.add_field(name="Gender", value=f"Male", inline=False)

  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.command(
  aliases=["nick"], help="Changes the nickname or remove it from a specific member"
)
@commands.has_permissions(change_nickname=True)
async def nickname(
  ctx: commands.Context, member: commands.MemberConverter = None, nickname: str = None
):
  user = member
  if member == None:
    user = ctx.author
  old = user.nick
  if old is None or old == None:
    old == None
  await user.edit(nick=nickname)
  if nickname == None and old != None:
    desc = f"Removed nickname ({old})"
  if nickname == None and old == None:
    desc = "This user doesn't have a nickname"
  if old == None and nickname != None:
    desc = f"Changed the nickname to ({nickname})"
  if old != None and nickname != None:
    desc = f"Changed the nickname from ({old}) to ({nickname})"

  em = nextcord.Embed(
    title="Nickname",
    description=desc,
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  em.set_thumbnail(url=user.display_avatar.url)
  await ctx.send(embed=em)


@bot.command(aliases=["joke"])
async def meme(ctx: commands.Context):

  subred = random.choice(["memes", "dankmemes"])

  msg = await ctx.send(
    embed=nextcord.Embed(
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
      title="Searching...",
      description="Please wait until the bot can find a meme on reddit",
    ).set_footer(
      icon_url=ctx.author.display_avatar.url,
      text=f"Requested by {ctx.author.name}",
    )
  )

  reddit = asyncpraw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="By Ahmed Amr",
  )

  subreddit = await reddit.subreddit(subred)

  all_subs = []
  top = subreddit.top(limit=100)
  async for submission in top:
    all_subs.append(submission)
  random_sub = random.choice(all_subs)

  name = random_sub.title
  url = random_sub.url

  em = nextcord.Embed(
    title=name, url=url, color=CUSTOM_COLOR, timestamp=datetime.datetime.utcnow()
  )
  em.set_image(url=url)

  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await msg.edit(embed=em)


@bot.event
async def on_member_join(member):
  server = member.guild
  if server.system_channel is not None:
    response = random.choice(
      [
        "Enjoy your stay!",
        "Feel free to chat with people here!",
        "You can now introduce yourself then start chatting!",
      ]
    )
    msg = await server.system_channel.send(
      f"Welcome {member.mention} in {server.name}!, {response}"
    )


@bot.event
async def on_member_remove(member):
  server = member.guild
  if server.system_channel is not None:
    response = random.choice(["Goodbye..", ":(", "Sad.."])
    msg = await server.system_channel.send(
      f"{member} has left {server.name}!, {response}"
    )


neko = NekosLifeClient()


@bot.command()
async def cuddle(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  result = await neko.image(SFWImageTags.CUDDLE)
  if member == ctx.author:
    title = "Cuddling yourself?"
  else:
    title = f"{ctx.author.name} has cuddled {member.name}!"
  em = nextcord.Embed(
    title=title,
    url=result.url,
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_image(url=result.url)
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.command()
async def kiss(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  result = await neko.image(SFWImageTags.KISS)
  if member == ctx.author:
    title = "Eww kissing yourself?"
  else:
    title = f"{ctx.author.name} has kissed {member.name}!"
  em = nextcord.Embed(
    title=title,
    url=result.url,
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_image(url=result.url)
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.command()
async def slap(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  result = await neko.image(SFWImageTags.SLAP)
  if member == ctx.author:
    title = "Don't slap yourself"
  if member == bot.user:
    title = random.choice(
      ["HOW DARE YOU TO SLAP ME?!", "WHAT HAVE YOU JUST DONE?!"]
    )
  else:
    title = f"{ctx.author.name} has slapped {member.name}!"
  em = nextcord.Embed(
    title=title,
    url=result.url,
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_image(url=result.url)
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.command()
async def poke(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  result = await neko.image(SFWImageTags.POKE)
  if member == ctx.author:
    title = "poking yourself?"
  else:
    title = f"{ctx.author.name} has poked {member.name}!"
  em = (
    nextcord.Embed(
      title=title,
      url=result.url,
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    .set_image(url=result.url)
    .set_footer(
      icon_url=ctx.author.display_avatar.url,
      text=f"Requested by {ctx.author.name}",
    )
  )
  await ctx.send(embed=em)


@bot.command(group="gay")
async def hug(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  result = await neko.image(SFWImageTags.HUG)
  if member == ctx.author:
    title = "hugging yourself?"
  else:
    title = f"{ctx.author.name} has hugged {member.name}!"
  em = nextcord.Embed(
    title=title,
    url=result.url,
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.set_image(url=result.url)
  em.set_footer(
    icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}"
  )
  await ctx.send(embed=em)


@bot.event
async def on_message(msg):
  if msg.author.id == bot.user.id:
    return

  stats = levelling.find_one({"id": msg.author.id})
  if not msg.author.bot:
    if stats is None:
      newuser = {"id": msg.author.id, "xp": 100}
      levelling.insert_one(newuser)
    else:
      xp = stats["xp"] + random.randrange(3, 7)
      levelling.update_one({"id": msg.author.id}, {"$set": {"xp": xp}})
      lvl = 0
      while True:
        if xp < ((50 * (lvl**2)) + (50 * (lvl))):
          break
        lvl += 1
      xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))
      if xp == 0:
        await msg.channel.send(
          f"Congrats {msg.author.mention}! You have levelled up to level {lvl}!"
        )
  if (
    msg.content == "<@!823231868328738826>"
    or msg.content == "<@823231868328738826>"
    or msg.content == "@Schtabtag#4097"
    or msg.content == "@Schtabtag"
  ):
    respond = ["Yes?", "What?", "Don't mention me again", "I'm here"]
    await msg.reply(random.choice(respond))
  if msg.content == "CLS" and msg.author.id == OWNER_ID:
    cls()
  if msg.content.startswith("code:\n```py") and msg.content.endswith("```"):
    mssg = msg.content[12:-4].replace("\n", ",")
    await msg.channel.send(mssg)
    try:
      try:
        await eval(mssg)
      except Exception as e:
        await msg.channel.send(e)
    except:
      try:
        eval()
      except Exception as e:
        await msg.channel.send(e)
  await bot.process_commands(msg)


@bot.command()
async def rank(ctx: commands.Context, user: commands.MemberConverter = None):
  if user == None:
    member = ctx.author
  else:
    member = user
  stats = levelling.find_one({"id": member.id})
  if stats is None:
    await ctx.send("You haven't send any messages go send some to earn XP")
  else:
    xp = stats["xp"]
    lvl = 0
    rank = 0
    while True:
      if xp < ((50 * (lvl**2)) + (50 * (lvl))):
        break
      lvl += 1
    xp -= (50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1))
    boxes = int((xp / (200 * ((1 / 2) * lvl))) * 20)
    rankings = levelling.find().sort("xp", -1)
    for x in rankings:
      rank += 1
      if stats["id"] == x["id"]:
        break

  realXP = f"{xp}/{int(200*((1/2)*lvl))}"
  realLVL = lvl
  realRank = f"{rank}/{ctx.guild.member_count}"
  realPercent = int((xp / (200 * (1 / 2 * lvl))) * 100)

  background = Editor("assets/bg.png")
  link = member.display_avatar.replace(size=1024, static_format="png").url
  profile = await load_image_async(str(link))
  profile = Editor(profile).resize((150, 150)).circle_image()
  poppins = Font.poppins(size=40)
  poppins_small = Font.poppins(size=20)

  square = Canvas((500, 500), "#AC27FA")
  square = Editor(square)
  square.rotate(30, expand=True)

  background.paste(square.image, (600, -250))
  background.paste(profile.image, (30, 30))

  background.rectangle((30, 220), width=650, height=40, fill="white", radius=20)
  background.bar(
    (30, 220),
    max_width=650,
    height=40,
    percentage=realPercent,
    fill="#AC27FA",
    radius=20,
  )
  background.text((200, 50), str(member), font=poppins, color="white")

  background.rectangle((200, 100), width=350, height=2, fill="#AC27FA")
  background.text((200, 125), f"Level : {realLVL}", font=poppins, color="white")
  background.text((200, 165), f"XP : {realXP}", font=poppins, color="white")

  file = nextcord.File(fp=background.image_bytes, filename="image.png")
  await ctx.send(file=file)


class TicTacToeButton(nextcord.ui.Button["TicTacToe"]):
  def __init__(self, x: int, y: int):
    super().__init__(style=nextcord.ButtonStyle.secondary, label="\u200b", row=y)
    self.x = x
    self.y = y

  async def callback(self, interaction: nextcord.Interaction):
    assert self.view is not None
    view: TicTacToe = self.view
    state = view.board[self.y][self.x]
    if state in (view.X, view.O):
      return

    if view.current_player == view.X:
      self.style = nextcord.ButtonStyle.danger
      self.label = "X"
      self.disabled = True
      view.board[self.y][self.x] = view.X
      view.current_player = view.O
      content = "It is now O's turn"
    else:
      self.style = nextcord.ButtonStyle.success
      self.label = "O"
      self.disabled = True
      view.board[self.y][self.x] = view.O
      view.current_player = view.X
      content = "It is now X's turn"

    winner = view.check_board_winner()
    if winner is not None:
      if winner == view.X:
        content = "X won!"
      elif winner == view.O:
        content = "O won!"
      else:
        content = "It's a tie!"

      for child in view.children:
        child.disabled = True

      view.stop()

    await interaction.response.edit_message(content=content, view=view)


class TicTacToe(nextcord.ui.View):
  children: List[TicTacToeButton]
  X = -1
  O = 1
  Tie = 2

  def __init__(self):
    super().__init__()
    self.current_player = self.X
    self.board = [
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
    ]

    for x in range(3):
      for y in range(3):
        self.add_item(TicTacToeButton(x, y))

  def check_board_winner(self):
    for across in self.board:
      value = sum(across)
      if value == 3:
        return self.O
      elif value == -3:
        return self.X

    for line in range(3):
      value = self.board[0][line] + self.board[1][line] + self.board[2][line]
      if value == 3:
        return self.O
      elif value == -3:
        return self.X

    diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
    if diag == 3:
      return self.O
    elif diag == -3:
      return self.X

    diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
    if diag == 3:
      return self.O
    elif diag == -3:
      return self.X

    if all(i != 0 for row in self.board for i in row):
      return self.Tie

    return None


@bot.command()
async def tic(ctx: commands.Context):
  await ctx.send("Tic Tac Toe: X goes first", view=TicTacToe())


@bot.command(help="Puts a given text in a frame")
async def frame(ctx: commands.Context, *, text):

  width = len(text)

  sentence = f"{text}"
  result = ""

  first = "```\n+-" + "-" * width + "-+\n"

  result += first

  for line in wrap(sentence, width):
    mid = "| {0:^{1}} |\n".format(line, width)
    result += mid

  last = "+-" + "-" * (width) + "-+\n```"
  result += last

  await ctx.send(result)


@bot.command()
async def guess(ctx: commands.Context):
  await ctx.channel.send("Guess a number between 1 and 10.")

  answer = random.randint(1, 10)
  attempts = 0
  while True:
    try:
      guess = await bot.wait_for("message", timeout=5.0)
      attempts += 1
    except asyncio.TimeoutError:
      return await ctx.channel.send(f"Sorry, you took too long it was {answer}.")
    if int(guess.content) == answer:
      await ctx.channel.send(
        f"Congratulations, You guessed it in {attempts} attempts!"
      )
      break
    else:
      if int(guess.content) > answer:
        await ctx.channel.send(f"Decrease your guessing")
      if int(guess.content) < answer:
        await ctx.channel.send(f"Increase your guessing")


@bot.slash_command(
  name="clear",
  description="Deletes a specific number of messages in a channel",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def clear(
  interaction: Interaction,
  amount: int = SlashOption(
    name="amount",
    description="The amount of messages to delete",
    default=1,
    required=False,
  ),
):
  if interaction.user.guild_permissions.manage_messages == True:
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
      f"Deleted {amount} messages successfully!", ephemeral=True
    )
  else:
    await interaction.response.send_message(
      "You don't have enough permissions to run this command"
    )


@bot.slash_command(
  name="ping",
  description="Displays the amount of latency of the bot in milliseconds",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def ping(interaction: Interaction):
  await interaction.response.send_message(f"Pong! in {round(bot.latency * 1000)}ms.")


@bot.slash_command(
  name="nickname",
  description="Changes the nickname or remove it from a specific member",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def nickname(
  interaction: Interaction,
  member: nextcord.Member = SlashOption(
    name="member",
    description="The member whose nickname will be changed/removed (default:command author)",
    required=False,
    default=None,
  ),
  nickname: str = SlashOption(
    name="nickname",
    required=False,
    description="The new nickname of the member (default:None)",
    default=None,
  ),
):
  if (
    interaction.user.guild_permissions.manage_nicknames == True
    or interaction.user.guild_permissions.change_nickname == True
  ):
    user = member
    if member == None:
      user = interaction.user
    old = user.nick
    if old is None or old == None:
      old == None
    await user.edit(nick=nickname)
    if nickname == None and old != None:
      desc = f"Removed nickname ({old})"
    if nickname == None and old == None:
      desc = "This user doesn't have a nickname"
    if old == None and nickname != None:
      desc = f"Changed the nickname to ({nickname})"
    if old != None and nickname != None:
      desc = f"Changed the nickname from ({old}) to ({nickname})"

    em = (
      nextcord.Embed(
        title="Nickname",
        description=desc,
        color=CUSTOM_COLOR,
        timestamp=datetime.datetime.utcnow(),
      )
      .set_footer(
        icon_url=interaction.user.display_avatar.url,
        text=f"Requested by {interaction.user.name}",
      )
      .set_thumbnail(url=user.display_avatar.url)
    )
    await interaction.response.send_message(embed=em)
  else:
    await interaction.response.send_message(
      "You don't have enough permissions to run this command"
    )


@bot.slash_command(
  name="avatar",
  description="Sends the avatar of a specific member",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def avatar(
  interaction: Interaction,
  member: nextcord.Member = SlashOption(
    name="member",
    description="The member whose avatar will be sent",
    required=False,
    default=None,
  ),
  format=SlashOption(
    name="format",
    required=False,
    description="The format of the member's image (default:PNG)",
    choices={
      "png": "png",
      "webp": "webp",
      "jpeg": "jpeg",
      "jpg": "jpg",
      "gif": "gif",
    },
    default="png",
  ),
):
  username = None
  avatar = None
  desc = ""
  if member == None:
    if interaction.user.display_avatar.is_animated() == False and format == "gif":
      avatar = interaction.user.display_avatar.replace(
        size=4096, format="png"
      ).url
      username = interaction.user.name
      desc = "Note:\nIt seems that the author of this command has chosen 'gif' as a format for the avatar image while having a static avatar so the format of the avatar wil be in 'png'"
    else:
      if (
        interaction.user.default_avatar.url
        == interaction.user.display_avatar.url
      ):
        avatar = interaction.user.display_avatar.replace(
          size=4096, format="png"
        ).url
        username = interaction.user.name
        desc = f"Note:\nIt seems that the author of this command has chosen '{format}' as a format for the avatar image while having a default avatar (standard Discord avatar) so the format of the avatar wil be in 'png'"
      else:
        avatar = interaction.user.display_avatar.replace(
          size=4096, format=format
        ).url
        username = interaction.user.name

  else:
    if member.display_avatar.is_animated() == False and format == "gif":
      avatar = member.display_avatar.replace(size=4096, format="png").url
      username = member.name
      desc = "Note:\nIt seems that the author of this command has chosen 'gif' as a format for the avatar image while having a static avatar so the format of the avatar wil be in 'png'"
    else:
      if member.default_avatar.url == member.display_avatar.url:
        avatar = member.display_avatar.replace(size=4096, format="png").url
        username = member.name
        desc = f"Note:\nIt seems that the author of this command has chosen '{format}' as a format for the avatar image while having a default avatar (standard Discord avatar) so the format of the avatar wil be in 'png'"
      else:
        avatar = member.display_avatar.replace(size=4096, format=format).url
        username = member.name
  em = nextcord.Embed(
    title=f"{username}'s avatar",
    description=desc,
    timestamp=datetime.datetime.utcnow(),
    color=CUSTOM_COLOR,
    url=avatar,
  )
  em.set_image(url=avatar)
  em.set_footer(
    text=f"Requested by {interaction.user}",
    icon_url=interaction.user.display_avatar.url,
  )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="translate",
  guild_ids=[OFFICIAL_GUILD_ID],
  description="Translates the passed argument into the passed language (Default:English)",
)
async def translate(
  interaction: Interaction,
  argument: str = SlashOption(
    name="argument",
    description="The argument which will be translated",
    required=True,
  ),
  source=SlashOption(
    name="source",
    default="auto",
    description="The language which the argument will be translated from",
    required=False,
    choices={
      "Auto detect language": "auto",
      "English - English": "en",
      "German - Deutsch": "de",
      "Arabic - عربي": "ar",
      "Spanish - español, castellano": "es",
      "Russian - русский": "ru",
      "Polish - Polski": "pl",
      "Italian - Italiano": "it",
      "Japanese - 日本語": "ja",
      "Irish - Gaeilge": "ga",
      "Hindi - हिन्दी, हिंदी": "hi",
      "Hebrew - עברית": "he",
      "French - Français": "fr",
      "Dutch - Nederlands": "nl",
      "Czech - česky, čeština": "cs",
      "Danish - Dansk": "da",
      "Chinese - 中文, Zhōngwén": "zh",
      "Persian - فارسی": "fa",
    },
  ),
  dest=SlashOption(
    name="dest",
    default="en",
    description="The language which the argument will be translated to",
    required=False,
    choices={
      "English - English": "en",
      "German - Deutsch": "de",
      "Arabic - عربي": "ar",
      "Spanish - español, castellano": "es",
      "Russian - русский": "ru",
      "Polish - Polski": "pl",
      "Italian - Italiano": "it",
      "Japanese - 日本語": "ja",
      "Irish - Gaeilge": "ga",
      "Hindi - हिन्दी, हिंदी": "hi",
      "Hebrew - עברית": "he",
      "French - Français": "fr",
      "Dutch - Nederlands": "nl",
      "Czech - česky, čeština": "cs",
      "Danish - Dansk": "da",
      "Chinese - 中文, Zhōngwén": "zh",
      "Persian - فارسی": "fa",
    },
  ),
):
  try:
    src = source
    dst = dest
    search = nextcord.Embed(
      title="Translating...",
      description='```py\n"Please wait..."```',
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    await interaction.response.send_message(embed=search)
    src = language_check.Check(src)
    dst = language_check.Check(dst)
    em = (
      nextcord.Embed(
        title="Translator",
        description=f"From ({src}) To ({dst})",
        color=CUSTOM_COLOR,
        timestamp=datetime.datetime.utcnow(),
      )
      .add_field(
        name="Source text", value=f'```py\n"{argument}"```', inline=False
      )
      .set_thumbnail(
        url="https://media.nextcordapp.net/attachments/893417057541050368/916290939893448714/Google_Translate_Icon.png"
      )
      .add_field(
        inline=False,
        name="Translated text",
        value=f'```py\n"{ts.google(argument,to_language=dest,from_language=source)}"```',
      )
    )
    em.set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
    await interaction.edit_original_message(embed=em)
  except:
    em = nextcord.Embed(
      description="Please check your arguments again.\nSyntax `trans src-lang dest-lang text`\nYou can read language abbreviations from [here](https://pastebin.com/PrxskfGq).",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
    await interaction.edit_original_message(embed=em)


@bot.slash_command(
  name="embed", description="Returns an embed", guild_ids=[OFFICIAL_GUILD_ID]
)
async def embed(
  interaction: Interaction,
  title: str = SlashOption(
    name="title", description="The title of the embed", required=True
  ),
  description: str = SlashOption(
    name="description",
    description="The description of the embed",
    required=False,
    default="",
  ),
  color: int = SlashOption(
    name="color",
    default=0x000000,
    description="The color of the embed",
    choices={
      "red": 0xFF0000,
      "green": 0x00FF00,
      "blue": 0x0000FF,
      "yellow": 0xFFFF00,
      "cyan": 0x00FFFF,
      "magenta": 0xFF00FF,
      "lime": 0x2EF429,
      "black": 0x000000,
      "white": 0xFFFFFF,
      "default purple color": CUSTOM_COLOR,
      "orange": 0xFF5E13,
      "gold": 0xCC9900,
      "pink": 0xFF007F,
      "purple": 0x663399,
    },
    required=False,
  ),
  url=SlashOption(
    name="url", description="The url of the embed", required=False, default=""
  ),
  footer=SlashOption(
    name="footer", description="The footer of the embed", required=False, default=""
  ),
):
  em = nextcord.Embed(
    colour=CUSTOM_COLOR, title=title, description=description, url=url
  ).set_footer(text=footer)
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="wikipedia",
  guild_ids=[OFFICIAL_GUILD_ID],
  description="Searches for a specific argument in wikipedia",
)
async def wiki(
  interaction: Interaction,
  argument: str = SlashOption(
    name="argument",
    description="The argument which will be searched for in wikipedia",
  ),
  sentences: int = SlashOption(
    default=1, name="amount", description="The number of sentences to search for"
  ),
  language=SlashOption(
    default="en",
    name="language",
    description="The language to search in",
    choices={
      "English - English": "en",
      "German - Deutsch": "de",
      "Arabic - عربي": "ar",
      "Spanish - español, castellano": "es",
      "Russian - русский": "ru",
      "Polish - Polski": "pl",
      "Italian - Italiano": "it",
      "Japanese - 日本語": "ja",
      "Irish - Gaeilge": "ga",
      "Hindi - हिन्दी, हिंदी": "hi",
      "Hebrew - עברית": "he",
      "French - Français": "fr",
      "Dutch - Nederlands": "nl",
      "Czech - česky, čeština": "cs",
      "Danish - Dansk": "da",
      "Chinese - 中文, Zhōngwén": "zh",
      "Persian - فارسی": "fa",
    },
  ),
):
  wiki_module.set_lang(language)
  search = nextcord.Embed(
    title="Wikipedia",
    description="Searching...",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  await interaction.response.send_message(embed=search)
  try:
    em = nextcord.Embed(
      title="Wikipedia",
      description=f"{wiki_module.summary(argument,sentences=sentences)}",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    )
    em.set_thumbnail(
      url="https://media.nextcordapp.net/attachments/893417057541050368/913832653927616562/2244px-Wikipedia-logo-v2.svg.png"
    )
  except:
    em = nextcord.Embed(
      title="Wikipedia",
      description=f"Couldn't find any result of that.",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
  await interaction.edit_original_message(embed=em)


@bot.slash_command(
  name="emojify",
  description="Converts given set of letters or numbers into emojis",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def emojify(
  interaction: Interaction,
  text: str = SlashOption(
    name="text",
    description="The text which will be converted into emojis",
    required=True,
  ),
):
  if len(text) < 120:
    real = text.lower()
    alphabet = [
      "a",
      "b",
      "c",
      "d",
      "e",
      "f",
      "g",
      "h",
      "i",
      "j",
      "k",
      "l",
      "m",
      "n",
      "o",
      "p",
      "q",
      "r",
      "s",
      "t",
      "u",
      "v",
      "w",
      "x",
      "y",
      "z",
    ]
    numbers = {
      "1": "one",
      "2": "two",
      "3": "three",
      "4": "four",
      "5": "five",
      "6": "six",
      "7": "seven",
      "8": "eight",
      "9": "nine",
      "0": "zero",
      "*": "asterisk",
      "#": "hash",
    }

    result = ""
    for each in real:
      if each == " ":
        result += "    "
      if each in alphabet:
        result += f":regional_indicator_{each}:"
      if each in numbers:
        result += f":{numbers[each]}:"

    em = nextcord.Embed(
      title="Emojify",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
      description=result,
    ).set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )

    await interaction.response.send_message(embed=em)
  else:
    await interaction.response.send_message(
      "Please make your argument less than 120 characters", ephemeral=True
    )


@bot.slash_command(
  name="calculate",
  description="Solves a given mathematical equation",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def calculate(
  interaction: Interaction,
  equation: str = SlashOption(
    name="equation",
    description="The mathematical equation which will be solved",
    required=True,
  ),
):
  try:
    dict = {
      "e": math.e,
      "pi": math.pi,
      "root": math.sqrt,
      "squareroot": math.sqrt,
      "sqrt": math.sqrt,
      "degrees": math.degrees,
      "radians": math.radians,
      "sin": sin,
      "cos": cos,
      "tan": tan,
      "asin": math.asin,
      "acos": math.acos,
      "atan": math.atan,
      "pow": math.pow,
      "power": math.pow,
      "fract": Fraction,
      "ratio": Fraction,
      "fraction": Fraction,
      "round": round,
    }
    problem = equation
    problem = problem.replace("^", "**")
    problem = problem.replace(":", "/")
    solve = str(eval(problem, dict))
    em = nextcord.Embed(
      title="Problem",
      description=f"```py\n{equation}\n```",
      color=CUSTOM_COLOR,
      timestamp=datetime.datetime.utcnow(),
    ).add_field(name="Solve", value=f" ```py\n{solve}\n```")
  except Exception as e:
    print(e)
    em = (
      nextcord.Embed(
        title="Calculator",
        description=f"Couldn't solve that.",
        color=CUSTOM_COLOR,
        timestamp=datetime.datetime.utcnow(),
      )
      .add_field(name="Error", value=f"```py\n{e}\n```")
      .set_footer(
        text=f"Requested by {interaction.user}",
        icon_url=interaction.user.display_avatar.url,
      )
    )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="say", description="Repeats a specific text", guild_ids=[OFFICIAL_GUILD_ID]
)
async def say(
  interaction: Interaction,
  text: str = SlashOption(
    name="text", description="Text that will be repeated by the bot", required=True
  ),
):
  await interaction.response.send_message(content=text)


@bot.slash_command(
  name="measure",
  description="Measures a specific set of digits or characters",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def measure(
  interaction: Interaction,
  text: str = SlashOption(
    name="text", description="The text that will be measured", required=True
  ),
):
  await interaction.response.send_message(
    f"Text : `{text}`\nThe number of characters in the text : `{len(text)}`"
  )


@bot.slash_command(
  name="userinfo",
  description="Gives information about a given user",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def userinfo(
  interaction: Interaction,
  user: nextcord.Member = SlashOption(
    name="user",
    required=False,
    default=None,
    description="The user who his/her information will be shown",
  ),
):
  member = user
  if member == None:
    member = interaction.user
  member = (
    await interaction.guild.query_members(user_ids=[member.id], presences=True)
  )[0]
  roles = [role.mention for role in member.roles[1:]]
  role = " ".join(roles)
  if len(roles) == 0:
    role = "No roles"
  date_format = "%a, %b %d, %Y %I:%M %p"
  av = member.display_avatar.url
  em = (
    nextcord.Embed(
      title="User Info:",
      timestamp=datetime.datetime.utcnow(),
      description=f"{member.name}'s information:",
      colour=CUSTOM_COLOR,
    )
    .add_field(name="ID", value=f"```py\n{member.id}```", inline=False)
    .add_field(
      name="USERNAME",
      value=f"```\n{member.name}#{member.discriminator}```",
      inline=False,
    )
    .add_field(
      name="JOINED SERVER ON",
      value=f"```\n{member.joined_at.strftime(date_format)}```",
      inline=False,
    )
    .add_field(
      name="CREATED ACCOUNT ON",
      value=f"```\n{member.created_at.strftime(date_format)}```",
      inline=False,
    )
    .add_field(name="ROLES", value=f"{role}", inline=False)
    .add_field(
      name="STRONGEST ROLE", value=f"{member.top_role.mention}", inline=False
    )
  )
  bot = "No"
  if member.bot:
    bot = "Yes"
  nick = "No nickname for this user"
  if member.nick != None:
    nick = member.nick
  em.add_field(name="BOT", value=f"```\n{bot}```", inline=False)
  status = "Can't access the status"
  if member.status is nextcord.Status.online:
    status = "Online"
  if member.status is nextcord.Status.offline:
    status = "Offline"
  if (
    member.status is nextcord.Status.dnd
    or member.status is nextcord.Status.do_not_disturb
  ):
    status = "Do not disturb"
  if member.status is nextcord.Status.idle:
    status = "Idle"
  if member.status is nextcord.Status.invisible:
    status = "Invisible"
  em.add_field(name="NICKNAME", value=f"```\n{nick}```", inline=False).add_field(
    name="CURRENT STATUS", value=f"```\n{member.status}```", inline=False
  )
  activity = "Nothing"
  if member.activity != None:
    activity = f"{member.activity.type.name} {member.activity.name} ({member.activity.details})"
  em.add_field(
    name="CURRENT ACTIVITY", value=f"```\n{activity}```", inline=False
  ).set_footer(
    text=f"Requested by {interaction.user.name}.",
    icon_url=interaction.user.display_avatar.url,
  ).set_thumbnail(
    url=av
  )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="hexadecimal",
  description="Converts a Hexadecimal color code into a RGB color and previews it",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def hexadecimal(
  interaction: Interaction,
  hex_code: str = SlashOption(
    name="hex_code",
    description="The code which will be converted into RGB color",
    required=True,
  ),
):
  try:
    result = ""
    final = "#"
    if hex_code.startswith("#"):
      final += hex_code.replace("#", "")
    if hex_code.startswith("#") == False:
      final += hex_code
    red = "0x" + final[1] + final[2]
    green = "0x" + final[3] + final[4]
    blue = "0x" + final[5] + final[6]
    red = int(red, base=0)
    green = int(green, base=0)
    blue = int(blue, base=0)
    link = f"https://singlecolorimage.com/get/{final[1:]}/900x900.png"
    em = nextcord.Embed(
      title=f"({red},{green},{blue})",
      description=f"{final.upper()}",
      color=nextcord.Color.from_rgb(red, green, blue),
      timestamp=datetime.datetime.utcnow(),
    ).set_image(url=link)
  except:
    em = nextcord.Embed(
      title=f"Error",
      description=f"Please provide a valid hexadecimal code like #7378F",
      color=0xFFFFFF,
      timestamp=datetime.datetime.utcnow(),
    ).set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="rgb",
  description="Converts a RGB color into Hexadecimal color code",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def rgb(
  interaction: Interaction,
  rgb_color=SlashOption(
    name="rgb_color",
    description="The RGB color which will be converted into a Hexadecimal color code",
    required=True,
  ),
):
  try:
    result = ""
    show = ""
    if rgb_color.startswith("(") and rgb_color.endswith(")"):
      fin = rgb_color[1:-1].split(",")
      show = rgb_color[1:-1]
    if rgb_color.startswith("(") == False and rgb_color.endswith(")") == False:
      fin = rgb_color.split(",")
      show = rgb_color
    fin = [int(n.strip()) for n in fin]

    for each in fin:
      hexadecimal = hex(each)[2:]
      if len(hexadecimal) == 1:
        hexadecimal = "0" + hexadecimal
      result += hexadecimal
    link = f"https://singlecolorimage.com/get/{result}/900x900.png"
    em = nextcord.Embed(
      title=f"#{result.upper()}",
      description=f"({show})",
      color=nextcord.Color.from_rgb(fin[0], fin[1], fin[2]),
      timestamp=datetime.datetime.utcnow(),
    ).set_image(url=link)
  except:
    em = nextcord.Embed(
      title=f"Error",
      description=f"Please provide a valid RGB color like (12,34,56)",
      color=0xFFFFFF,
      timestamp=datetime.datetime.utcnow(),
    ).set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="frame",
  description="Puts a given text in a frame",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def frame(
  interaction: Interaction,
  text: str = SlashOption(
    name="text", description="The text which will be put in a frame", required=True
  ),
  width: str = SlashOption(
    name="width",
    description="The width of the frame which the text will be put in",
    required=False,
    default=None,
  ),
):
  if width == None:
    realwidth = len(text)
  else:
    realwidth = width
  sentence = f"{text}"
  result = ""

  first = "```\n+-" + "-" * realwidth + "-+\n"

  result += first

  for line in wrap(sentence, realwidth):
    mid = "| {0:^{1}} |\n".format(line, realwidth)
    result += mid

  last = "+-" + "-" * (realwidth) + "-+\n```"
  result += last

  await interaction.response.send_message(result)


@bot.slash_command(
  name="count",
  description="Displays a clickable button that increases its value when clicking on it",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def count(interaction: Interaction):
  await interaction.response.send_message("Count", view=view())


@bot.slash_command(
  name="8ball",
  description="Replies to polar (yes/no) question with one of the standard 8ball responses from Wikipedia",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def eightball(
  interaction: Interaction,
  question: str = SlashOption(
    name="question",
    description="The polar question (yes/no question) which will be answered",
    required=True,
  ),
):
  embed = (
    nextcord.Embed(
      title="8ball", timestamp=datetime.datetime.utcnow(), color=CUSTOM_COLOR
    )
    .set_footer(
      text=f"Requested by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
    )
    .add_field(name="Question", value=question, inline=False)
    .add_field(name="Answer", value=random.choice(responds))
  )
  await interaction.response.send_message(embed=embed)


@bot.slash_command(
  name="reverse",
  description="Reverses specific text which is given as an argument",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def reverse(
  interaction: Interaction,
  text: str = SlashOption(
    name="text", description="The text which will be reversed", required=True
  ),
):
  result = text[::-1]
  await interaction.response.send_message(result)


@bot.slash_command(
  name="uwu",
  description="Converts a specific given text into uwu-text~",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def uwu(
  interaction: Interaction,
  text: str = SlashOption(
    name="text",
    description="The specific text which will be converted into uwu-text~",
    required=True,
  ),
):
  real = text.lower()
  for each in real:
    real = real.replace("thing", "fing")
    real = real.replace("l", "w")
    real = real.replace("r", "w")
  await interaction.response.send_message(real + "~")


@bot.slash_command(
  name="whereami",
  description="Displays the current channel and server which the user is in",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def whereami(interaction: Interaction):
  await interaction.response.send_message(
    f"You are in ({interaction.guild.name}) in {interaction.channel.mention} channel"
  )


@bot.slash_command(
  name="statistics",
  description="Displays information about Schtabtag",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def statistics(interaction: Interaction):
  username = bot.user
  servers = len(bot.guilds)
  nextcordV = nextcord.__version__
  process = psutil.Process(os.getpid())
  ram = (process.memory_info().rss / 1000) / 1000
  ram = "{:.2f}".format(ram)
  ram = str(ram) + "mb"
  ver = platform.python_version()
  em = nextcord.Embed(
    title=f"Bot's statstics",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  em.add_field(
    name=":crown:OWNER'S ID:crown:", value=f"```py\n{OWNER_ID}```", inline=True
  )
  em.add_field(
    name="<:py:893420197132771378>PYTHON VERSION<:py:893420197132771378>",
    value=f"```py\n{ver}```",
    inline=True,
  )
  ping = bot.latency * 1000
  ping = round(ping)
  em.add_field(name=":zap:LATENCY:zap:", value=f'```py\n"{ping}ms"```', inline=True)
  em.add_field(name="FULL USERNAME", value=f"```py\n{username}```", inline=True)
  em.add_field(
    name=":school:SERVERS:school:", value=f"```py\n{servers}```", inline=True
  )
  em.add_field(
    name=":bar_chart:RAM USAGE:bar_chart:", value=f'```py\n"{ram}"```', inline=True
  )
  em.add_field(
    name="<:nextcord:901845590663643147>DISCORD VERSION<:nextcord:901845590663643147>",
    value=f"```py\n{nextcordV}```",
    inline=True,
  )
  em.add_field(
    name=":computer:HOST:computer:",
    value=f'```py\n"Being hosted on my owner\'s laptop."```',
    inline=False,
  )
  em.add_field(
    name=":timer:ELAPSED TIME:timer:",
    value=f"```py\n{int((time.time() - begin) / 60)} minutes\n```",
  )
  date_format = "%a, %b %d, %Y %I:%M %p"
  em.set_footer(
    text=f"Requested by {interaction.user.name}.",
    icon_url=interaction.user.display_avatar.url,
  )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="serverinfo",
  description="Displays information about the current server",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def serverinfo(interaction: Interaction):
  date_format = "%a, %b %d, %Y %I:%M %p"
  server = interaction.guild
  name = server.name
  em = nextcord.Embed(
    title="Server info",
    description=f"Information about {name}",
    color=CUSTOM_COLOR,
    timestamp=datetime.datetime.utcnow(),
  )
  id = server.id
  description = server.description
  icon = server.icon.url
  if interaction.guild.banner != None:
    banner = server.banner.url
    em.set_image(url=banner)
  else:
    banner = None
  humans = len(server.humans)
  bots = len(server.bots)
  owner = server.owner
  created = server.created_at
  em.add_field(name="ID", value=f"```\n{id}```", inline=False)
  em.add_field(name="NAME", value=f"```\n{name}```", inline=False)
  em.add_field(
    name="CREATED ON",
    value=f"```\n{created.strftime(date_format)}```",
    inline=False,
  )
  em.add_field(name="HUMANS", value=f"```\n{humans}```", inline=False)
  em.add_field(name="DESCRIPTION", value=f"```\n{description}```", inline=False)
  em.add_field(name="BOTS", value=f"```\n{bots}```", inline=False)
  em.add_field(name="OWNER", value=f"```\n{owner}```", inline=False)
  em.set_thumbnail(url=icon)
  em.set_footer(
    icon_url=interaction.user.display_avatar.url,
    text=f"Requested by {interaction.user.name}",
  )
  await interaction.response.send_message(embed=em)


@bot.slash_command(
  name="ban",
  description="Bans a specific member from the current server",
  guild_ids=[OFFICIAL_GUILD_ID],
)

async def ban(
  interaction: Interaction,
  user: nextcord.Member = SlashOption(
    name="user", description="The user who will be banned", required=True
  ),
  reason: str = SlashOption(
    name="reason", description="The reason of banning the user", required=False
  ),
):
  if interaction.user.guild_permissions.ban_members == True:
    member = await bot.fetch_user(user.id)
    em = (
      nextcord.Embed(
        title="BAN", color=CUSTOM_COLOR, timestamp=datetime.datetime.utcnow()
      )
      .add_field(name=member, value=member.id)
      .add_field(name="REASON", value=reason)
      .set_footer(
        text=f"Requested by {interaction.user.author.name}",
        icon_url=interaction.user.display_avatar.url,
      )
      .set_thumbnail(url=member.display_avatar.url)
    )
    await interaction.response.send_message(embed=em)
    await interaction.guild.ban(user=user, reason=reason)
  else:
    await interaction.response.send_message(
      "You don't have enough permissions to run this command"
    )


@bot.slash_command(
  name="kick",
  description="Kicks a specific member from the current server",
  guild_ids=[OFFICIAL_GUILD_ID],
)
async def kick(
  interaction: Interaction,
  user: nextcord.Member = SlashOption(
    name="user", description="The user who will be kicked", required=True
  ),
  reason: str = SlashOption(
    name="reason", description="The reason of kicking the user", required=False
  ),
):
  if interaction.user.guild_permissions.kick_members == True:
    member = await bot.fetch_user(user.id)
    em = (
      nextcord.Embed(
        title="KICK", color=CUSTOM_COLOR, timestamp=datetime.datetime.utcnow()
      )
      .add_field(name=member, value=member.id)
      .add_field(name="REASON", value=reason)
      .set_footer(
        text=f"Requested by {interaction.user.author.name}",
        icon_url=interaction.user.display_avatar.url,
      )
      .set_thumbnail(url=member.display_avatar.url)
    )
    await interaction.response.send_message(embed=em)
    await interaction.guild.kick(user=user, reason=reason)
  else:
    await interaction.response.send_message(
      "You don't have enough permissions to run this command"
    )


class HelpEmbed(nextcord.Embed):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.timestamp = datetime.datetime.utcnow()
    text = (
      "Use help [command] for more information | <> is required | [] is optional"
    )
    self.set_footer(text=text)
    self.color = CUSTOM_COLOR


class MyHelp(commands.HelpCommand):
  def __init__(self):
    super().__init__(
      command_attrs={
        "help": "The help command for the bot",
        "aliases": ["commands"],
      }
    )

  async def send(self, **kwargs):
    await self.get_destination().send(**kwargs)

  async def send_bot_help(self, mapping):
    ctx = self.context
    embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
    embed.set_thumbnail(url=ctx.me.display_avatar.url)
    usable = 0

    for cog, commands in mapping.items():
      if filtered_commands := await self.filter_commands(commands):
        amount_commands = len(filtered_commands)
        usable += amount_commands
        if cog:
          name = cog.qualified_name
          description = cog.description or "No description"
        else:
          name = "No"
          description = "Commands with no category"

        embed.add_field(
          name=f"{name} Category [{amount_commands}]", value=description
        )

    embed.description = f"{len(bot.commands)} commands | {usable} usable"

    await self.send(embed=embed)

  async def send_command_help(self, command):
    signature = self.get_command_signature(command)
    embed = HelpEmbed(
      title=signature, description=command.help or "No help found..."
    )

    if cog := command.cog:
      embed.add_field(name="Category", value=cog.qualified_name)

    can_run = "No"
    with contextlib.suppress(commands.CommandError):
      if await command.can_run(self.context):
        can_run = "Yes"

    embed.add_field(name="Usable", value=can_run)

    if command._buckets and (cooldown := command._buckets._cooldown):
      embed.add_field(
        name="Cooldown",
        value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
      )

    await self.send(embed=embed)

  async def send_help_embed(self, title, description, commands):
    embed = HelpEmbed(title=title, description=description or "No help found...")

    if filtered_commands := await self.filter_commands(commands):
      for command in filtered_commands:
        embed.add_field(
          name=self.get_command_signature(command),
          value=command.help or "No help found...",
        )

    await self.send(embed=embed)

  async def send_group_help(self, group):
    title = self.get_command_signature(group)
    await self.send_help_embed(title, group.help, group.commands)

  async def send_cog_help(self, cog):
    title = cog.qualified_name or "No"
    await self.send_help_embed(
      f"{title} Category", cog.description, cog.get_commands()
    )


bot.help_command = MyHelp()

bot.run(TOKEN)
