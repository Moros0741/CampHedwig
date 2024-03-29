import disnake, typing, random, datetime, asyncio, json
from disnake.ext import tasks, commands
from random import choice
from typing import Optional
from Cogs import database as db


class Drops(commands.Cog):
    """Snowpocalypse commands"""
    def __init__(self, bot):
        self.bot = bot

    async def send_drop(self, drop):
        guild = self.bot.get_guild(drop[0])
        channel = guild.get_channel(drop[1])
        emoji = self.bot.get_emoji(928282118939901952)
        contents = open("./data/components.json", 'r').read()
        c = json.loads(contents)
        mess = random.choice(c["messages"])
        image = random.choice(c["images"])
        
        embed = disnake.Embed(
            description=f"Oh. What's this? Snowflakes {emoji} are falling from the sky! Let's see how many we can catch. React below to catch it",
            color=self.bot.color
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
                winner = disnake.Embed(
                    title="You caught a Snowflake!", 
                    description=mess,
                    color=self.bot.color
                )
                winner.set_thumbnail(url=image)
                winner.add_field(name="\u200b", value=f"Congrats, {user.mention} you've caught `{int(count) + 1}` {emoji} snowflake(s)!")
                await msg.edit(embed = winner, delete_after=30)
                await db.update_count(guild.id, user.id)
        
        except asyncio.TimeoutError:
            try:
                message = await channel.fetch_message(msg.id)
                await message.delete()
            except disnake.Forbidden:
                pass
            
    @tasks.loop(seconds = 10)
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
                    Now = datetime.datetime.strptime(timenow, '%m %d, %Y %H:%M:%S')
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

    @commands.command(description="See how many snowflakes you or another user have caught!")
    async def count(self, ctx, member: Optional[disnake.Member]=None):
        if member is None:
            member = ctx.author

        result = await db.fetch_user(ctx.guild.id, member.id)

        embed = disnake.Embed(
            description=f"{member.mention} has claimed `{result[2]}` <a:smores:875460650762113064> Marshmallows!",
            color=self.bot.color
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=['lb', 'top'], description="See who has collected the most snowflakes at Hogwarts!")
    async def leaderboard(self, ctx):
        results = await db.fetch_all(ctx.guild.id)
        leaderboards = []
        n = 1
        for result in results[0:10]: 
            member = f"<@!{int(result[0])}>"
            leaderboards.append("**{:^4}.** `{:,}` - {:^16} ".format(n, result[1], member))
            n += 1

        embed = disnake.Embed(
            title=f"{ctx.guild.name.title()}'s Leaders",
            color=self.bot.color
        )

        embed.add_field(name="Top 10", value="{}".format('\n'.join(leaderboards)), inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.message.delete()
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Drops(bot))