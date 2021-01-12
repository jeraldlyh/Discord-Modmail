# Overview
This module allows you to setup a modmail in the server. It serves as a shared inbox for server moderators to communicate with users in a seamless way.

# How does it work?
Whenever a user sends a direct message to the bot, a channel/thread will be created in the designated category. Moderators are able to respond to the user via the channel which users will receive the replies from their DMs thereafter.

# Commands Usage
- `-setup` -> Automatically sets up the modmail module in the server
- `-disable` -> Close all current threads and disable modmail
- `-close` -> Resolve and close the current threaed
- `-block <userID>` -> Blocks specified user and prevent them from utilising modmail
- `-unblock <userID>` -> Unblocks specified user
- `-help` -> Display available commands for moderators

# Notes
- Moderators must be awarded the `Server Support` role to gain permission for the modmail module.
- Manually configure your discord ID in the script at **Lines 93 & 183**.
- All threads are available under the catgegory titled `📋 Support`.
- Tweak and configure the category name accordingly to your preference in the script by replacing the default name stated above in the script.
