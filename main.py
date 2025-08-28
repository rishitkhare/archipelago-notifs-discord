# This example requires the 'message_content' intent.

import discord
from discord.ext import tasks
import os

# custom modules
from archipelago_site import get_recent_archipelago_actions, check_for_new_archipelago_actions
from notifications import parse_usr_msg, save_notifs_to_file


bot_token = os.environ['BOT_TOKEN']
tracker_site_ip = os.environ["TRACKER_SITE_URL"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

recorded_actions = get_recent_archipelago_actions()
updates_channel = None

@tasks.loop(seconds=5.0)
async def archipelago_updates():
    global recorded_actions
    global updates_channel
    global current_notifications

    # if an updates channel has not been specified, skip over the routine for now.
    # This allows updates that were added before the channel was specified to stack up
    # and not be missed.
    if not updates_channel:
        return

    # scrape the data from the webpage in the most recent visit. Then, compare it against the data
    # from the last visit to see what was newly added
    updated_actions = get_recent_archipelago_actions()
    newly_added = check_for_new_archipelago_actions(recorded_actions, updated_actions)

    notifs_list_updated = False

    for update in newly_added.values():
        # send the regular update
        msg_content = f"***{update['Finder']}*** found ***\"{update['Item']}\"*** for ***{update['Receiver']}!!!***"
        print(f'sending this update:\n{msg_content}\n')
        await updates_channel.send(msg_content)

        # check for any matching notifications
        indicesToRemove = []
        for index, notification in current_notifications:
            if(notification.itemName == update['Item'].lower() and notification.playerName == update['Receiver'].lower()):
                await updates_channel.send("@"+notification.username+" update['Finder'] has found "+update['Item']+" for "+update['Receiver']+"!")
                indicesToRemove.append(index)

        if (len(indicesToRemove) > 0):
            notifs_list_updated = True

        indicesToRemove.sort(reverse=True)
        for index in indicesToRemove:
            current_notifications.pop(index)

    if(notifs_list_updated):
        save_notifs_to_file()

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

    if(updates_channel and message.channel == updates_channel):
        await parse_usr_msg(message)

    if client.user.mentioned_in(message):
        updates_channel = message.channel
        await message.channel.send('Archipelago updates will now occur in this channel!')


client.run(bot_token)