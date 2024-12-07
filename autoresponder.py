import discord
from log import send_webhook
from discord.ext import commands

autoresponder = False
autoresponder_msg = ""
autoresponder_users = set()

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def autoresponder(self, ctx, *, stat=None):
        global autoresponder
        global autoresponder_msg
        global autoresponder_users

        if stat is None:
            autoresponder = False
            autoresponder_msg = ""
            autoresponder_users = set()
            await ctx.reply("Autoresponder has been turned off.")
            self.asd("Autoresponder has been turned off.")
        else:
            autoresponder = True
            autoresponder_msg = stat
            await ctx.reply(f"Autoresponder has been turned on with message: {stat}")
            self.asd(f"Autoresponder has been turned on with message: {stat}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        global autoresponder
        global autoresponder_users

        if autoresponder:
            if not isinstance(message.channel, discord.DMChannel):
                return
            
            user_id = message.author.id
            if user_id not in autoresponder_users:
                autoresponder_users.add(user_id)
                await message.reply(autoresponder_msg)
                self.asd(f"Sent autoresponder acknoledgement to {message.author.mention} ({user_id}).")
            else:
                pass

    def asd(self, message):
        send_webhook(message)

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))