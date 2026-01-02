from random import randint
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import logging
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio

load_dotenv()
token = os.getenv("ROHAN_DISCORD_TOKEN")
if(not token):
    raise Exception("DISCORD_TOKEN not found in environment variables")

# change default command prefix to #


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

timezone = ZoneInfo("America/Los_Angeles")
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    
    if bot.user:
        print(f"{bot.user.name} is now running!")

# reply "heck you" when pinged
@bot.event
async def on_message(message: discord.Message):
    # Always process commands first
    await bot.process_commands(message)

    # Ignore messages from the bot itself
    if message.author == bot.user:
        await asyncio.sleep(1)
        if randint(1, 100) <= 85: # X% chance to reply
            reply_content = "stop pinging yourself <@958167615833006121>"
            if message.content.startswith(reply_content):
                reply_content = "stop ponging yourself <@958167615833006121>"
            await message.reply(reply_content)
        return

    # Whitelisted user ID
    allowed_user_id = 518551211604049920

    # Check if the author is the allowed user
    if message.author.id != allowed_user_id:
        if "praise dungewar the almighty" in message.content.lower():
            return  # Do nothing if the phrase is found

        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your message needs to have ```praise dungewar the almighty``` to be allowed", delete_after=5)
            print(f"Deleted message from {message.author} (ID: {message.author.id})")
        except discord.Forbidden:
            print(f"Could not delete message from {message.author}. Missing 'Manage Messages' permission.")
        except discord.NotFound:
            # Message was already deleted, probably by another bot or moderator
            pass
        return # Stop further on_message processing for this message

    # Original functionality for whitelisted user and bot interactions
    if bot.user and bot.user.mentioned_in(message):
        await message.reply(f"heck you", mention_author=False)

# !say
@bot.command()
async def s(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete()

def current_log_path():
    date = datetime.now(timezone).strftime("%m-%d-%Y")
    return f"logs/{date}.txt"

# where to send reminders
target_context = None

# # reminder every 5 mins
# @tasks.loop(minutes=5)
# async def reminders():
#     if target_context:
#         await target_context.send(f"-# what are you doing {target_context.author.mention}")

# # !start
# @bot.command()
# async def start(ctx):
#     global target_context
#     if reminders.is_running():
#         await ctx.send("already running")
#     else:
#         target_context = ctx
#         reminders.start()
#         await ctx.send("started")

# # !stop
# @bot.command()
# async def stop(ctx):
#     if reminders.is_running():
#         reminders.stop()
#         await ctx.send("stopped")
#     else:
#         await ctx.send("not running")

# # !setdelay
# @bot.command()
# async def setdelay(ctx, minutes: float):
#     reminders.change_interval(minutes=minutes)
#     clamped = max(0.1, minutes)
#     reminders.change_interval(minutes=clamped)
#     await ctx.send(f"delay changed to {clamped} minutes")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name: str):
    """Creates a new text channel."""
    guild = ctx.guild
    try:
        await guild.create_text_channel(channel_name)
        await ctx.send(f"Successfully created channel: #{channel_name}")
    except discord.Forbidden:
        await ctx.send("I don't have the required permissions to create channels.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to create channel. An error occurred: {e}")

@create_channel.error
async def create_channel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the `manage_channels` permission to use this command.")

@bot.command()
async def my_permissions(ctx):
    """Shows the bot's permissions in the current channel."""
    # The bot's member object in the current guild
    bot_member = ctx.guild.me
    
    # Get the permissions for the bot in the current channel
    permissions = ctx.channel.permissions_for(bot_member)
    
    # Create a list of permissions
    permission_list = [perm for perm, value in permissions if value]
    
    # Format the list into a nice string
    permissions_str = "\n".join(permission_list).title()
    
    # Create an embed to display the permissions
    embed = discord.Embed(
        title="My Permissions in this Channel",
        description=permissions_str,
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed)


@bot.command(name='change-nickname', aliases=['cn'])
@commands.has_permissions(manage_nicknames=True)
async def change_nickname(ctx, member: discord.Member, *, nickname: str):
    """Changes a member's nickname."""
    try:
        await member.edit(nick=nickname)
        await ctx.send(f"Successfully changed {member.mention}'s nickname to `{nickname}`.")
    except discord.Forbidden:
        await ctx.send("I don't have the required permissions to change nicknames.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change nickname. An error occurred: {e}")

@change_nickname.error
async def change_nickname_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the `manage_nicknames` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!change-nickname @member <new nickname>`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f"Could not find a member named `{error.argument}`.")


@bot.command(name='set-bot-nickname')
@commands.has_permissions(manage_nicknames=True)
async def set_bot_nickname(ctx, *, nickname: str):
    """Changes the bot's own nickname in the server."""
    try:
        await ctx.guild.me.edit(nick=nickname)
        await ctx.send(f"My nickname is now `{nickname}`.")
    except discord.Forbidden:
        await ctx.send("I don't have the `Change Nickname` permission.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change my nickname. An error occurred: {e}")

@set_bot_nickname.error
async def set_bot_nickname_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the `manage_nicknames` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!set-bot-nickname <new nickname>`")


@bot.command(name='delete-message', aliases=['delmsg'])
async def delete_message(ctx: Context, message_id: int):
    """Deletes a message by its ID if the user has permission or is the author."""
    try:
        message = await ctx.channel.fetch_message(message_id)

        if isinstance(ctx.author, discord.Member):
        # Check if the user has manage_messages perm OR is the author of the message
            # can_delete = ctx.channel.permissions_for(ctx.author).manage_messages or message.author == ctx.author

            # if not can_delete:
            #     await ctx.send("You can only delete your own messages, or you need the `Manage Messages` permission.")
            #     return

            await message.delete()
            await ctx.send(f"Successfully deleted message with ID: `{message_id}`.", delete_after=5)

    except discord.Forbidden:
        await ctx.send("I don't have the `Manage Messages` permission to do that.")
    except discord.NotFound:
        await ctx.send(f"Could not find a message with the ID `{message_id}` in this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to delete the message. An error occurred: {e}")

@delete_message.error
async def delete_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!delete-message <message_id>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Message ID must be a number.")


@bot.command(name='delete-all-containing', aliases=['delcon'])
@commands.has_permissions(manage_messages=True)
async def delete_all_containing(ctx, *, keyword: str):
    """Deletes all messages in the channel containing a specific keyword."""
    await ctx.message.delete() # Delete the command message
    
    deleted_count = 0
    
    # Let the user know the process is starting
    status_message = await ctx.send(f"Searching for messages containing `{keyword}`... this may take a while.")
    
    try:
        # Iterate over the channel's history
        async for message in ctx.channel.history(limit=None):
            if keyword.lower() in message.content.lower():
                try:
                    await message.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    await status_message.edit(content="I am missing the `Manage Messages` permission to delete messages.")
                    return
                except discord.HTTPException as e:
                    await status_message.edit(content=f"An error occurred while deleting messages: {e}")
                    return
    
        await status_message.edit(content=f"Done! Deleted {deleted_count} message(s) containing `{keyword}`.")
    except Exception as e:
        await status_message.edit(content=f"An unexpected error occurred: {e}")

@delete_all_containing.error
async def delete_all_containing_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the `manage_messages` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!delete-all-containing <keyword>`")


# @bot.command()
# async def doing(ctx, *, message):
#     timestamp = ctx.message.created_at.astimezone(timezone).strftime('%I:%M:%S %p')
#     with open(current_log_path(), "a") as f:
#         f.write(f'{timestamp}: {message}\n')
#     await ctx.message.add_reaction('🧀')
    

bot.run(token, log_handler=handler, log_level=logging.DEBUG)