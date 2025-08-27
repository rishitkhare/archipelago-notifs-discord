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

current_notifications = []

class NotificationStruct:
    def __init__(self, username, itemName, playerName):
        self.username = username
        self.itemName = itemName
        self.playerName = playerName

@tasks.loop(seconds=5.0)
async def archipelago_updates():
    global recorded_actions
    global updates_channel
    global current_notifications

    if not updates_channel:
        return

    updated_actions = get_recent_archipelago_actions()
    newly_added = check_for_new_archipelago_actions(recorded_actions, updated_actions)

    for update in newly_added.values():
        msg_content = f"***{update['Finder']}*** found ***\"{update['Item']}\"*** for ***{update['Receiver']}!!!***"
        print(f'sending this update:\n{msg_content}\n')
        await updates_channel.send(msg_content)

        #check for any matching notifications
        indicesToRemove = []
        for index, notification in current_notifications:
            if(notification.itemName == update['Item'].lower() and notification.playerName == update['Receiver'].lower()):
                await updates_channel.send("@"+notification.username+" update['Finder'] has found "+update['Item']+" for "+update['Receiver']+"!")
                indicesToRemove.append(index)

        indicesToRemove.sort(reverse=True)
        for index in indicesToRemove:
            current_notifications.pop(index)

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
        await check_for_notification(message)

    if client.user.mentioned_in(message):
        updates_channel = message.channel
        await message.channel.send('Archipelago updates will now occur in this channel!')

async def check_for_notification(message):
    global current_notifications

    args = message.content.substring(1).split(" ")
    argsLen = args.len()
    if(argsLen > 0 and args[0].lower() == "notify"):
        if(argsLen == 1):
            await print_error_message()
        else if(argsLen >= 2):
            if(args[1].lower() == "add"):
                #create a new notification (if it does not already exist)
                if(argsLen != 4):
                    await print_error_message()
                else:
                    username = message.author.name
                    itemName = args[1].lower()
                    playerName = args[2].lower()

                    duplicateNotif = False
                    for notification in current_notifications:
                        if(notification.itemName == itemName and notification.playerName == playerName):
                            duplicateNotif = True
                            break
                    
                    if(duplicateNotif):
                        await message.channel.send("Error: notification already exists!")
                    else:
                        current_notifications.append(NotificationStruct(username, itemName, playerName))
                        await message.channel.send("Notification added!")

            else if(args[1].lower() == "remove"):
                #remove an existing notification (if a matching one exists)
                if(argsLen != 4):
                    await print_error_message()
                else:
                    itemName = args[1].lower()
                    playerName = args[2].lower()

                    notifIndex = -1
                    for index, notification in current_notifications:
                        if(notification.itemName == itemName and notification.playerName == playerName):
                            notifIndex = index
                            break
                    
                    if(notifIndex == -1):
                        await message.channel.send("Error: notification not found!")
                    else:
                        current_notifications.pop(notifIndex)
                        await message.channel.send("Notification removed!")
            
            else if (args[1].lower() == "list"):
                #list all active notifications
                if(current_notifications.len() == 0):
                    await message.channel.send('There are no active notifications!')
                else:
                    notifsListStr = "Active notifications:"
                    for notification in current_notifications:
                        notifsListStr += ("\n-Will ping "+notification.username+" when \""+notification.itemName+"\" is given to player: \""+notification.playerName+"\"")
                    await message.channel.send(notifsListStr)
            else:
                await print_error_message()

async def print_error_message():
    await message.channel.send('Invalid format! Please use one of the following\n!notify add [ItemName] [PlayerName]\n!notify remove [ItemName] [PlayerName]\n!notify list')

client.run(bot_token)