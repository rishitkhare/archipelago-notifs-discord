# This example requires the 'message_content' intent.

import discord
from discord.ext import tasks
import os
from archipelago_site import get_recent_archipelago_actions, check_for_new_archipelago_actions

bot_token = os.environ['BOT_TOKEN']
tracker_site_ip = os.environ["TRACKER_SITE_URL"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

recorded_actions = get_recent_archipelago_actions()
updates_channel = None

@tasks.loop(seconds=40.0)
async def archipelago_updates():
    global recorded_actions
    global updates_channel

    if not updates_channel:
        return

    updated_actions = get_recent_archipelago_actions()
    newly_added = check_for_new_archipelago_actions(recorded_actions, updated_actions)

    for update in newly_added.values():
        msg_content = f"***{update['Finder']}*** found ***\"{update['Item']}\"*** for ***{update['Receiver']}!!!***"
        print(f'sending this update:\n{msg_content}\n')
        await updates_channel.send(msg_content)

    recorded_actions = updated_actions

    print("performed routine check")

@client.event
async def on_ready():
    global updates_channel
    print(f'We have logged in as {client.user}')

    # updates_channel = client.guilds[0].system_channel

    archipelago_updates.start()

@client.event
async def on_message(message):
    global updates_channel

    if client.user.mentioned_in(message):
        updates_channel = message.channel
        await message.channel.send('Archipelago updates will now occur in this channel!')

client.run(bot_token)