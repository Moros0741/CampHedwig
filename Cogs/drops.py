import discord, typing, random, datetime, asyncio, json
from discord.ext import tasks, commands
from discord.ext.commands import has_permissions, has_guild_permissions, MissingPermissions
from random import choice
from typing import Optional
from Cogs import database as db


class Drops(commands.Cog):
    """<a:jumpys:871708733355474964> Smores Season Commands<a:jumpys:871708733355474964>
    """
    def __init__(self, bot):
        self.bot = bot

    async def send_drop(self, drop):
        guild = self.bot.get_guild(drop[0])
        channel = guild.get_channel(drop[1])
        emoji = self.bot.get_emoji(875460650762113064)
        contents = open("./Cogs/components.json", 'r').read()
        c = json.loads(contents)
        mess = random.choice(c["drops"]["messages"])
        image = random.choice(c["drops"]["images"])
        
        embed = discord.Embed(
            description=f"Oh. What's this? A {emoji} has been found! Let's see how many you can eat. React below to claim it",
            color=discord.Colour.dark_green()
        )
        
        msg = await channel.send(embed=embed)
        await msg.add_reaction(emoji)

        def check(reaction, user):
            return reaction.message == msg and user != self.bot.user
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=300)
            if reaction.emoji == emoji:
                count = await db.fetch_user(guild.id, user.id)
                if count is None:
                    count = 0
                else:
                    count = count[2]
                await msg.clear_reactions()
                winner = discord.Embed(
                    title="You claimed the Marshmallow!", 
                    description=mess,
                    color=discord.Colour.gold()
                )
                winner.set_image(url=image)
                winner.add_field(name="\u200b", value=f"Congrats, {user.mention} you've ate `{int(count) + 1}` {emoji} marshmallows")
                await msg.edit(embed = winner, delete_after=30)
                await db.update_count(guild.id, user.id)
        
        except asyncio.TimeoutError:
            try:
                message = await channel.fetch_message(msg.id)
                await message.delete()
            except discord.Forbidden:
                pass
            
    @tasks.loop(seconds = 30)
    async def DropTask(self):
        timenow = datetime.datetime.utcnow().strftime('%m %d, %Y %H:%M:%S')
        drops = await db.fetch_all_drops()
        for drop in drops:

            if drop[2] is None or drop[2] == "None":
                pass
            else:
                if int(drop[2]) == 0:
                    pass
                else:
                    Delta = datetime.timedelta(seconds=int(drop[2]))
                    Last = datetime.datetime.strptime(drop[3], "%m %d, %Y %H:%M:%S")
                    Now = datetime.datetime.utcnow().strptime(timenow, '%m %d, %Y %H:%M:%S')
                    Next = Last + Delta
                    if Next <= Now and drop[4] == 'True':
                        await Drops.send_drop(self, drop)
                        await db.set_last_drop(int(drop[0]))
                    else:
                        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is Ready!")
        await self.bot.wait_until_ready()
        await Drops.DropTask.start(self)

    @commands.command(description="See how many marshmallows you or another member have ate.")
    async def eaten(self, ctx, member: Optional[discord.Member]=None):
        if member is None:
            member = ctx.author

        result = await db.fetch_user(ctx.guild.id, member.id)

        embed = discord.Embed(
            description=f"{member.mention} has claimed `{result[2]}` <a:smores:875460650762113064> Marshmallows!",
            color=discord.Colour.dark_green()
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=['lb', 'top'], description="See who has collected the most <a:smores:875460650762113064> in the Server")
    async def leaderboard(self, ctx):
        """|<a:jumpys:871708733355474964> Leaderboards <a:jumpys:871708733355474964>"""
        results = await db.fetch_all(ctx.guild.id)
        leaderboards = []
        leaderboards.append("{:^4} | {:^5} | {:^16}".format("NO.#", "Count", "Member"))
        leaderboards.append("-----+-------+-----------------")
        n = 1
        for result in results[0:9]: 
            member = ctx.guild.get_member(int(result[0]))
            leaderboards.append("{:^4} | {:^5} | {:^16} ".format(n, result[1], member.display_name if len(str(member.display_name)) < 16 else str(member.display_name)[:13] + "..."))
            n += 1

        embed = discord.Embed(
            title=f"{ctx.guild.name.title()}'s Leaders",
            description="```{}```".format('\n'.join(leaderboards)),
            color=discord.Colour.dark_green()
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Drops(bot))