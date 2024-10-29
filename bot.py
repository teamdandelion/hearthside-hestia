import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up intents - being more explicit about DM-related intents
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True
intents.guilds = True
intents.messages = True  # Ensure we can see messages

class HearthsideBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Hearthside Community Bot',
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),  # Safe defaults
        )
    
    async def setup_hook(self):
        """Load cogs when bot starts up"""
        await self.load_extension('cogs.anonymous')
        print("Loaded anonymous messaging cog")
    
    async def on_ready(self):
        """Called when bot is fully ready"""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Connected to {len(self.guilds)} guilds:')
        for guild in self.guilds:
            print(f'- {guild.name} (ID: {guild.id})')
        print('------')
    
    async def on_message(self, message):
        """Debug logging for messages"""
        if isinstance(message.channel, discord.DMChannel):
            print(f"DM received from {message.author} (ID: {message.author.id})")
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Enhanced error handling"""
        print(f"Error occurred: {type(error)} - {error}")  # Debug logging
        
        if isinstance(error, commands.PrivateMessageOnly):
            await ctx.send("This command can only be used in DMs!")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("I don't have the required permissions to do that!")
        elif isinstance(error, discord.Forbidden):
            print(f"Forbidden error in {ctx.channel.type} with {ctx.author}")
            await ctx.send("I don't have permission to do that! This might be a DM permission issue.")
        else:
            print(f'Unexpected error: {error}')
            await ctx.send("An error occurred. Please try again later.")

async def main():
    # Create bot instance
    bot = HearthsideBot()
    
    # Start the bot with our token
    async with bot:
        await bot.start(os.getenv('DISCORD_TOKEN'))

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())