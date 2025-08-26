# Archipelago Notifications Bot ("The Argo")

This is the source code for a discord bot that scrapes from an archipelago.gg sphere tracker once deployed and sends discord message updates whenever a new item is collected. To deploy it, use 
the [Discord Developer Portal](https://discord.com/developers) to register a bot to use their API.

When running the script, make sure the following packages are installed to your venv:
 - [discord.py](https://pypi.org/project/discord.py/)
 - [lxml](https://pypi.org/project/lxml/)

And make sure the following environment variables are defined (such that `os.environ()` will access these variables)
 - `BOT_TOKEN` (The unique token assigned to your bot. Can be found in developer portal)
 - `TRACKER_SITE_URL` (The url of the sphere tracker site)

Deploy the bot to a platform of your choosing and have fun! ***Please note that the bot does not currently support tracking of multiple games nor does it support
being in multiple servers at this time.***

## Example:
<img width="491" height="250" alt="Screenshot 2025-08-25 at 8 35 40 PM" src="https://github.com/user-attachments/assets/b50447c6-c262-4d2e-ad95-512b4366c3a6" />
