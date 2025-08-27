# This module stores important data and functions associated with
# the "notifications" feature. This feature allows users to subscribe
# to notifications on specific items and then receive pings when
# said item is obtained by another player.

from collections import namedtuple

current_notifications = []

Notification = namedtuple('Notification', ['username', 'itemName', "playName"])

async def add_notification(username, itemName, playerName, channel):
    duplicateNotif = False
    for notification in current_notifications:
        if (notification.itemName == itemName and notification.playerName == playerName):
            duplicateNotif = True
            break

    if (duplicateNotif):
        await channel.send("Error: notification already exists!")
    else:
        current_notifications.append(Notification(username, itemName, playerName))
        await channel.send("Notification added!")

async def remove_notification(itemName, playerName, channel):
    notifIndex = -1
    for index, notification in current_notifications:
        if (notification.itemName == itemName and notification.playerName == playerName):
            notifIndex = index
            break

    if (notifIndex == -1):
        await channel.send("Error: notification not found!")
    else:
        current_notifications.pop(notifIndex)
        await channel.send("Notification removed!")

async def list_notifications(channel):
    # list all active notifications
    if (len(current_notifications) == 0):
        await channel.send('There are no active notifications!')
    else:
        notifsListStr = "Active notifications.py:"
        for notification in current_notifications:
            notifsListStr += (
                    "\n-Will ping " + notification.username + " when \"" + notification.itemName + "\" is given to player: \"" + notification.playerName + "\"")
        await channel.send(notifsListStr)

async def parse_usr_msg(message):
    global current_notifications

    args = message.content[1].split(" ")
    argsLen = args.len()

    if (argsLen > 0 and args[0].lower() == "notify"):
        if (argsLen == 1):
            await send_usage_help_msg(message.channel)
            return

        match args[1].lower():
            case "add":
                # create a new notification (if it does not already exist)

                if (argsLen != 4):
                    await send_usage_help_msg(message.channel)
                    return

                username = message.author.name
                itemName = args[1].lower()
                playerName = args[2].lower()

                await add_notification(username,itemName,playerName,message.channel)

            case "remove":
                # remove an existing notification (if a matching one exists)
                if (argsLen != 4):
                    await send_usage_help_msg(message.channel)
                    return

                itemName = args[1].lower()
                playerName = args[2].lower()

                await remove_notification(itemName, playerName, message.channel)

            case "list":
                await list_notifications(message.channel)
            case _:
                await send_usage_help_msg(message.channel)

async def send_usage_help_msg(channel):
    await channel.send('Unrecognized command. Usage:\n!notify add [ItemName] [PlayerName]\n!notify remove [ItemName] [PlayerName]\n!notify list')