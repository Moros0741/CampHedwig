import disnake, os, dotenv
from disnake.ext import commands
from dotenv import load_dotenv
from Cogs import database as db

intents = disnake.Intents.default()
intents.members = True

async def get_prefix(bot, message):
    if message.guild is not None:
        r = await db.fetch_prefix(message.guild.id)
        if r is not None:
            return commands.when_mentioned_or(r[0])(bot, message)
        elif r is None:
            return commands.when_mentioned_or("=")(bot, message)
            await db.add_prefix(message.guild.id, "=")
        else:
            return commands.when_mentioned_or("=")(bot, message)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            activity=disnake.Activity(name="Snowman Contest", type=5),
            help_command=None,
            intents = intents,
        )
        self.user_ids = [765324522676682803, 694322536397406238, 700057705951395921]
        self.color = disnake.Colour.from_rgb(160, 216, 241)
        self.colors = [(91, 170, 209), (121, 219, 250)]

bot = MyBot()

load_dotenv()

TOKEN = os.getenv('TOKEN')

@bot.event
async def on_ready():
    print(f"{bot.user} has logged onto Discord")

@bot.command(hidden=True)
async def reload(ctx, extension):
    try:
        bot.reload_extension(f"Cogs.{extension}")
        await ctx.send(f":white_check_mark: Extension `{extension}` has been reloaded.")
    except Exception as e:
        exec = "{} : {}".format(extension, e)
        print(exec)
        await ctx.send(f":x: Failed to reload extension `{extension}`. Refer to console for error printout.")

startup_extensions = ['general', 'drops']

for extension in startup_extensions: 
    try:
        bot.load_extension(f"Cogs.{extension}")
    except Exception as e:
        exec = "{} : {}".format(extension, e)
        print(exec)


try:
    bot.run(TOKEN)
except Exception as e:
    print(e)
    print("ERROR: Bot failed to start. This is probably due to an invalid token.")