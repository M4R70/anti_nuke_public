# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
from collections import defaultdict
from collections import deque
import datetime
import asyncio


class Main(commands.Cog):
    """The description for Main goes here."""

    def __init__(self, bot):
        self.bot = bot
        self.cache = defaultdict(lambda: [])
        self.last_kick_entry_id = 0
        self.last_ban_entry_id = 0
        self.time_limit = 150
        self.ban_treshold = 50

    # @commands.Cog.listener()
    # async def on_message(self,message):
    #     pass

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     print(member)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        entry = await search_entry(guild, user, discord.AuditLogAction.ban)
        if entry is None or self.last_ban_entry_id == entry.id:
            return
        self.last_ban_entry_id = entry.id
        await self.anti_nuke(entry)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        entry = await search_entry(member.guild, member, discord.AuditLogAction.kick)
        if entry is None or self.last_kick_entry_id == entry.id:
            return
        self.last_kick_entry_id = entry.id
        await self.anti_nuke(entry)

    async def anti_nuke(self, entry):
        mod = entry.user
        print(f"mod {mod}")
        mod_id = mod.id
        now = datetime.datetime.now()
        self.cache[mod_id].append(now)
        self.cache[mod_id] = [x for x in self.cache[mod_id] if (now - x).total_seconds() < self.time_limit]
        print(f"cache bans: {len(self.cache[mod_id])}")
        if len(self.cache[mod_id]) >= self.ban_treshold:
            await mod.send("Hey, it looks like you banned a lot of people, in a short amount of time, "
                           "so i kicked you to avoid having the server nuked, no hard feelings. Feel free to "
                           "rejoin the server and contact Marto to clear this up")
            await mod.kick(reason="suspected nuke bot")

    @commands.command()
    async def hi(self, ctx):
        await ctx.send(':wave:')


async def search_entry(guild, target_user, action):
    t = 1
    entry = None
    while entry is None:
        async for e in guild.audit_logs(action=action, limit=10):
            if e.target.id == target_user.id:
                return e
        await asyncio.sleep(t)
        t += t
        if t > 60:
            return None


def setup(bot):
    bot.add_cog(Main(bot))
