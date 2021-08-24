import discord, typing, asyncio, random, datetime, json
from discord.ext import commands
from discord.ext.commands import has_any_role
from typing import Optional, Union
from random import choice, randint
from Cogs import database as db

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is ready!")

    @commands.command(description="Shows command help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Command Help", 
            description="Anything in:\n`[]` is Optional \n`<>` is mandatory.",
            color=discord.Colour.dark_green()
        )
        embed.add_field(
            name=f"`{ctx.prefix}leaderboards` | Aliases: `{ctx.prefix}top`, `{ctx.prefix}lb` ", 
            value="Displays the top ten members in the server.", 
            inline=False
        )
        embed.add_field(
            name=f"`{ctx.prefix}eaten [@Member]`| Aliases: `None`", 
            value="Display how many marshmallows you have eaten, or another user if mentioned.", 
            inline=False
        )

        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(name='set', description="Set prefix, dropdchannel, droptime, on,  off")
    async def _set(self, ctx, marker, *, setting: Union[discord.TextChannel, str, discord.Emoji]):
        if ctx.author.id not in self.bot.user_ids:
            await ctx.send("You are not one of the accepted users of that command.", delete_after=5)
        
        else:
            if marker.lower() == 'prefix' and isinstance(setting, str):
                prefix = setting.split(' ')
                await db.add_prefix(ctx.guild.id, prefix[0])
                response = f'Set `{prefix[0]}` as the server prefix'
            
            elif marker.lower() == 'dropchannel':
                await db.set_drop_channel(ctx.guild.id, setting.id)
                response = f"Drops will now spawn in {setting.mention}"
            
            elif marker.lower() == 'droptime':
                if isinstance(setting, int):
                    time = setting * 60
                
                elif isinstance(setting, str):
                    time_convert = {"s":1, "m":60, "h":3600,"d":86400}
                    time= int(setting.strip("smhd")) * time_convert[str(setting[-1])]

                await db.set_msg_time(ctx.guild.id, time)
                response = f"Set Drop time to `{setting}`"
            
            elif marker.lower() == 'drop':
                if setting.lower() == 'on':
                    await db.toggle_drop(ctx.guild.id, 'True')
                    response = "Drops `Enabled`"

                elif setting.lower() == "off":
                    await db.toggle_drop(ctx.guild.id, 'False')
                    response = "Drops `Disabled`"
            

            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description=response, color=discord.Colour.dark_green()), delete_after=10)

    @commands.command(description="Help embed for setting up drops")
    async def sethelp(self, ctx):
        if ctx.author.id in self.bot.user_ids:
            embed = discord.Embed(
                title="Setup Help",
                description="Anything in: \n`[]` is Optional \n`<>` is Mandatory",
                color=discord.Colour.dark_green()
            )
            embed.add_field(
                name=f"`{ctx.prefix}set <marker> <setting>`", 
                value=f"""Sets various drop settings. 
                         
                         **Markers**
                         > `dropchannel` - *Mentioned channel* 
                         > `droptime` - *Time as a number and letter ex: `1m`, `1h` or `1d` (m = Minutes, h = Hours, d = Days.)*
                         > `drop` - *Turns drops on or off.* Ex: `{ctx.prefix}set drop on`
                         > `prefix` - *Sets the prefix for the server.* Ex: `{ctx.prefix}set prefix <new_prefix>`
                        """,
                inline=False
            )
            embed.add_field(
                name =f"`{ctx.prefix}settings` | Aliases: `None`",
                value="*View this server's current drop settings and information.",
                inline=False
            )
            await ctx.message.delete()
            await ctx.send(embed=embed)

    @commands.command(description="view the current drop settings")
    async def settings(self, ctx):
        r = await db.fetch_drop(ctx.guild.id)
        if r[4] == 'True':
            color = discord.Colour.dark_green()
        elif r[4] == 'False':
            color = discord.Colour.dark_red()
        else:
            color = discord.Colour.random()
        embed = discord.Embed(
            title=f"{ctx.guild}'s Drop Settings", 
            color=color
        )
        embed.add_field(name="Drop Status", value="<a:green:848971267050176513> `Enabled`" if r[4] != 'False' else "<a:red:848971266676883506> `Disabled`", inline=True)
        m, s = divmod(int(r[2]), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        embed.add_field(name = '\u200b', value = '\u200b', inline=True)
        embed.add_field(name="Drop Time", value="{}d : {}h : {}m : {}s".format(d, h, m, s), inline=True)
        embed.add_field(name='Drop Channel', value = f"<#{r[1]}>", inline=True)
        embed.add_field(name= '\u200b', value='\u200b', inline=True)
        embed.add_field(name="Last Drop", value =r[3], inline=True)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(descripiton="Dump components files.")
    async def dump(self, ctx):
        if ctx.author.id in self.bot.user_ids:
            fp = open("./Cogs/components.json", 'r').read()
            f = json.loads(fp)
            images = f["drops"]["images"]
            messages = f["drops"]["messages"]

            msg = await ctx.send("Are you sure you want to do this? It will dump all contents into chat.?")
            emojis = ['✅', '❌']
            for emoji in emojis:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and user != self.bot.user and str(reaction.emoji) in emojis

            
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 120)

            
                if str(reaction.emoji) == '✅':
                    for image in images:
                        embed = discord.Embed(
                            description=f"[Image Link]({image})",
                            color=discord.Colour.dark_green()
                        )
                        embed.set_image(url=image)
                    
                        await ctx.send(embed=embed)
                    
                    if len(messages) < 10:

                        embed = discord.Embed(
                            title="Messages",
                            color=discord.Colour.dark_green()
                        )
                        for message in messages:
                            embed.add_field(name='\u200b', value=message, inline=False)
                        
                        await ctx.send(embed = embed)
                    
                    elif len(messages) > 10 and len(messages) < 50:
                        
                        for message in messages:
                            embed = discord.Embed(
                                description=message,
                                color=discord.Colour.dark_green()
                            )
                            await ctx.send(embed = embed)
                    
                    await ctx.send("✅ All Components have been dumped.")
                
                elif str(reaction.emoji) == "❌":
                    await ctx.send("❌ Cancelled component dump")
            
            except asyncio.TimeoutError:
                try:
                    await msg.delete()
                except:
                    pass
        else:
            await ctx.reply("You do not have the permissions required to access this command.", delete_after=10)

def setup(bot):
    bot.add_cog(General(bot))