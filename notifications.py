# This module stores important data and functions associated with
# the "notifications" feature. This feature allows users to subscribe
# to notifications on specific items and then receive pings when
# said item is obtained by another player.

from collections import namedtuple
import shlex
import pickle

filename = "saved_notifs.json"
current_notifications = []

Notification = namedtuple('Notification', ['userIDs', 'usernames', 'itemName', "playerName"])

def load_notifs_from_file():
    if(os.path.isfile(filename)):
        with open(filename, 'rb') as file:
            current_notifications = pickle.load(file)
    else:
        current_notifications = []

def save_notifs_to_file():
    file = open(filename, 'wb+')
    pickle.dump(current_notifications, file)

async def add_notification(user, itemName, playerName, channel):
    userID = user.id
    username = user.name

    existingNotifIndex = -1
    for i, notification in enumerate(current_notifications):
        if (notification.itemName == itemName and notification.playerName == playerName):
            existingNotifIndex = i
            break

    if existingNotifIndex != -1:
        existingNotif = current_notifications[existingNotifIndex]

        if userID in existingNotif.userIDs:
            await channel.send("You are already signed up for this notification!")
            return

        existingNotif.userIDs.append(userID)
        existingNotif.usernames.append(username)

        await channel.send("Notification added!")
    else:
        current_notifications.append(Notification([userID], [username], itemName, playerName))
        await channel.send("Notification added!")

    save_notifs_to_file()

async def remove_notification(user, itemName, playerName, channel):
    userID = user.id
    username = user.name

    notifIndex = -1
    for index, notification in enumerate(current_notifications):
        if (notification.itemName == itemName and notification.playerName == playerName):
            notifIndex = index
            break

    if (notifIndex == -1):
        await channel.send("This notification does not exist!")
    else:
        notifObj = current_notifications[notifIndex]

        if not userID in notifObj.userIDs:
            await channel.send("Cannot remove: You are not signed up for this notification!")
            return

        # remove the entire notification object or just remove that user (if they are not the only one subscribed)
        if len(notifObj.usernames) == 1:
            current_notifications.pop(notifIndex)
        else:
            notifObj.userIDs.remove(userID)
            notifObj.usernames.remove(username)

        await channel.send("Notification removed!")
    save_notifs_to_file()

async def list_notifications(channel):
    print("running list command")

    # list all active notifications
    if (len(current_notifications) == 0):
        await channel.send('There are no active notifications!')
    else:
        notifsListStr = "Active notifications:\n```"
        for notification in current_notifications:
            notifsListStr += f"\n* {notification.itemName} ==> {notification.playerName} (notifies "

            for i in range(len(notification.usernames)):
                if i != 0:
                    notifsListStr += ", "

                notifsListStr += f"{notification.usernames[i]}"
            notifsListStr += ")"
        notifsListStr += "```"
        await channel.send(notifsListStr)

async def parse_usr_msg(message):
    global current_notifications

    args = shlex.split(message.content[1:])
    argsLen = len(args)
    print(args)

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

                user = message.author
                itemName = args[2].lower().strip()
                playerName = args[3].lower().strip()

                await add_notification(user,itemName,playerName,message.channel)

            case "remove":
                # remove an existing notification (if a matching one exists)
                if (argsLen != 4):
                    await send_usage_help_msg(message.channel)
                    return

                itemName = args[2].lower().strip()
                playerName = args[3].lower().strip()

                await remove_notification(message.author, itemName, playerName, message.channel)

            case "list":
                await list_notifications(message.channel)
            case _:
                await send_usage_help_msg(message.channel)

async def send_usage_help_msg(channel):
    await channel.send('Unrecognized command. Usage:\n!notify add [ItemName] [PlayerName]\n!notify remove [ItemName] [PlayerName]\n!notify list')


load_notifs_from_file()