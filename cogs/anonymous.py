from discord.ext import commands
import discord
import re
from typing import Optional, Tuple

class AnonymousMessaging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_link_pattern = r'https?://discord\.com/channels/(\d+)/(\d+)/(\d+)'
        self.pending_replies = {}

    def find_channel(self, channel_name: str) -> Optional[discord.TextChannel]:
        """Find channel by name in the Hearthside server"""
        # Remove '#' if user included it
        channel_name = channel_name.lstrip('#')
        
        # Since Hestia should only be in Hearthside server, use first (and only) guild
        if not self.bot.guilds:
            print("Bot is not in any guilds!")
            return None
            
        guild = self.bot.guilds[0]
        print(f"Looking for channel '{channel_name}' in {guild.name}")
        
        # Try exact match first
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        
        if not channel:
            # Try case-insensitive match
            channel = discord.utils.get(guild.text_channels, 
                                      name=channel_name.lower())
            
        if channel:
            print(f"Found channel: {channel.name}")
        else:
            print(f"No channel found matching '{channel_name}'")
            
        return channel

    @commands.dm_only()
    @commands.command(name="anon")
    async def direct_anonymous_message(self, ctx, channel_name: str, *, message: str):
        """Post an anonymous message to a channel using !anon command"""
        print(f"Received anon command for channel: {channel_name}")
        
        # Find the channel
        target_channel = self.find_channel(channel_name)
        
        if not target_channel:
            # List available channels to help the user
            guild = self.bot.guilds[0]
            available_channels = [f"#{c.name}" for c in guild.text_channels 
                                if c.permissions_for(guild.me).send_messages]
            
            response = "❌ I couldn't find that channel. Available channels are:\n"
            response += "\n".join(available_channels)
            await ctx.send(response)
            return
            
        try:
            embed = discord.Embed(
                description=message,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Anonymous Message")
            
            await target_channel.send(embed=embed)
            await ctx.send(f"✅ Your anonymous message has been posted in #{target_channel.name}!")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to post in that channel.")

    # ... rest of the existing code for message link handling ...
    
    @direct_anonymous_message.error
    async def anon_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            guild = self.bot.guilds[0]
            available_channels = [f"#{c.name}" for c in guild.text_channels 
                                if c.permissions_for(guild.me).send_messages]
            
            response = "Please use the format: `!anon channel-name Your message`\n"
            response += "Available channels:\n"
            response += "\n".join(available_channels)
            await ctx.send(response)

async def setup(bot):
    await bot.add_cog(AnonymousMessaging(bot))