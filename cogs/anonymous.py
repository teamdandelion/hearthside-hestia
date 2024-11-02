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
        channel_name = channel_name.lstrip('#')

        if not self.bot.guilds:
            print("Bot is not in any guilds!")
            return None

        guild = self.bot.guilds[0]
        print(f"Looking for channel '{channel_name}' in {guild.name}")

        channel = discord.utils.get(guild.text_channels, name=channel_name.lower())
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

        target_channel = self.find_channel(channel_name)

        if not target_channel:
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message links and replies"""
        if message.author.bot:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        print("\n=== Message Debug Info ===")
        print(f"Message ID: {message.id}")
        print(f"Author: {message.author}")
        print(f"Content: {message.content[:50]}...")

        if message.reference:
            print("\n=== Reply Info ===")
            print(f"Referenced Message ID: {message.reference.message_id}")
            try:
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
                print(f"Referenced Message Content: {referenced_message.content[:50]}...")
            except:
                print("Couldn't fetch referenced message")

        print("\n=== Current Pending Replies ===")
        for key, value in self.pending_replies.items():
            print(f"Key: {key}")
            print(f"Target Message Channel: {value.channel}")
            print(f"Target Message Content: {value.content[:50]}...")

        # Handle replies
        if message.reference:
            print("\n=== Processing Reply ===")
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            print(f"Looking for reference message ID: {referenced_message.id}")

            # Try to find the original target message
            target_message = None
            for stored_id, target in self.pending_replies.items():
                if stored_id == referenced_message.id:
                    target_message = target
                    break

            if target_message:
                print("Found target message! Sending anonymous reply...")
                try:
                    embed = discord.Embed(
                        description=message.content,
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text="Anonymous Reply")

                    await target_message.reply(embed=embed)
                    await message.add_reaction('✅')
                    # Clean up the stored message
                    self.pending_replies = {k:v for k,v in self.pending_replies.items() if k != referenced_message.id}
                    print("Successfully sent anonymous reply")
                except Exception as e:
                    print(f"Error sending reply: {str(e)}")
                    await message.channel.send(f"❌ Error sending reply: {str(e)}")
            else:
                print("No matching target message found")

        # Handle message links
        elif 'discord.com/channels/' in message.content:
            print("\n=== Processing Message Link ===")
            try:
                matches = re.finditer(self.message_link_pattern, message.content)
                for match in matches:
                    guild_id, channel_id, message_id = map(int, match.groups())
                    print(f"Found link to - Guild: {guild_id}, Channel: {channel_id}, Message: {message_id}")

                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        await message.channel.send("❌ I couldn't find that channel!")
                        continue

                    try:
                        target_message = await channel.fetch_message(message_id)
                        # Send confirmation and store the confirmation message ID
                        confirmation = await message.channel.send("✅ I've registered this message. Reply to this message with your anonymous response!")
                        self.pending_replies[confirmation.id] = target_message
                        print(f"Stored target message with confirmation ID: {confirmation.id}")
                    except discord.NotFound:
                        await message.channel.send("❌ I couldn't find that message!")
                    except discord.Forbidden:
                        await message.channel.send("❌ I don't have permission to read that message!")
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        await message.channel.send(f"❌ Error: {str(e)}")

            except Exception as e:
                print(f"Error processing link: {str(e)}")
                await message.channel.send("❌ Error processing that message link!")


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
