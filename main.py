# This example requires the 'message_content' intent.

import discord
from discord.ext import tasks
import os

# custom modules
from archipelago_site import get_recent_archipelago_actions, check_for_new_archipelago_actions
from notifications import parse_usr_msg, current_notifications, save_notifs_to_file, load_notifs_from_file, load_patrons_from_bk


bot_token = os.environ['BOT_TOKEN']
tracker_site_ip = os.environ["TRACKER_SITE_URL"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

recorded_actions = get_recent_archipelago_actions()
updates_channel = None

@tasks.loop(seconds=20.0)
async def archipelago_updates():
    global recorded_actions
    global updates_channel
    global current_notifications
    global current_burger_king_patrons

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

        # check for any matching notifications
        existingNotif = None
        for notification in current_notifications:
            if(notification.itemName == update['Item'].lower() and notification.playerName == update['Receiver'].lower()):
                existingNotif = notification

                # grab a list of every ping
                pinglist = ""
                for i in range(len(notification.usernames)):
                    if i != 0:
                        pinglist += ", "

                    pinglist += f"<@{notification.userIDs[i]}>"

                await updates_channel.send(f"# ARCHIPELAGO UPDATE!\n{pinglist}\n***{update['Finder']}*** has found ***{update['Item']}*** for ***{update['Receiver']}***!")
                # if an important item has been found, the receiver can become a burger king leaver
                if update['Receiver'] in current_burger_king_patrons:
                    current_burger_king_patrons.remove(update['Receiver'])

                break

        if existingNotif:
            current_notifications.remove(existingNotif)
            save_notifs_to_file()

        else:
            # nobody signed up for pings, so give the message normally
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

    if message.content.startswith("!") and updates_channel and message.channel == updates_channel:
        await parse_usr_msg(message)

    if client.user.mentioned_in(message):
        updates_channel = message.channel
        await message.channel.send('Archipelago updates will now occur in this channel!')


load_notifs_from_file()
load_patrons_from_bk()

client.run(bot_token)