from discord.ext import commands
from os import environ
from lib.database import Database
import discord


class Zect(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(environ.get('PREFIX', '/')),
            help_command=None,
        )
        self.db = Database(self)

    async def on_ready(self):
        status = discord.Game("Vocaleague by.Zect")
        await self.change_presence(activity=status)
