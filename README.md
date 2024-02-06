# Discord Bot: Email-Verification

This bot serves as verification bot for email verification and automatic assignment of roles upon verification. It stores the mapping of users to email addresses in a SQLite database and therefore should only be used in contexts where this information is necessary, such as on private university discord servers.

1. Create a new discord server

2. Add at least the following channels
	- PUBLIC_CHANNEL: Depending on a user's discord setting, it might not be possible for the bot to write a private message. The user will then be notified in this channel to adapt his settings accordingly. The channel should be visible to unverified users.
	- AUTH_CHANNEL: The bot will inform about unusual verification behaviour in this channel (wrong token sent, timeouts). This channel should be private, unless you want everyone to know about a user's inability to copy and paste.
	- VER_CHANNEL: This channel empowers the admins to change the role, which should be assigned after successful verification. This might be useful if tutors join a discord prior to students etc.

3. Add the required roles: Admin, tutor, student and unverified

4. Decide for an e-mail address from which the bot should send verification e-mails
	- Required: possibility to automatically send e-mails from an application. I used gmail for that.

5. Create a bot on the discord developer portal: https://discord.com/developers/applications
	- Bot Permissions: Just give the bot administrator rights or figure out something else by yourself
	- Privileged Gateway Intents: "message content intent" and "server members intent"
	- Copy your bot's token

2. Put all the data in the .env file, the IDs are accessible when switching to discords developer mode

	TOKEN="the token of your bot from the discord developer website"
	BOT_PASSWORD="password for the email account"  
	SMTP_SERVER=""  
	SMTP_PORT=""  
	BOT_EMAIL="email address"  
	DB="desired name of the database, that stores the user-id, username, emial, token for verification and verified status"  
	GUILD_ID="id of the server"  
	PUBLIC_CHANNEL_ID=""  
	AUTH_CHANNEL_ID=""  
	VER_CHANNEL_ID=""  
	ADMIN_ID="id of the admin role"  
	TUTOR_ID=""  
	STUDENT_ID=""  
	NOT_VERIFIED_ID=""  

7. Add the Bot to your server
	- Create URL in OAuth2 - URL Generator: Scopes "Bot" and in Bot Permissions "Administrator"
	- Copy URL and choose your server

8. For whatever reason, the bot requires to get assigned admin permissions via the admin role (or an additional bot role with admin rights) to be able to set the users' roles. So just give it to him unless you find another solution to this problem.

9. Run your bot by executing the main.py file (python main.py). The bot should now write DMs to users that join your server and you should be able to restart the verification process manually by typing "verify" in the private chat with the bot. It should first ask you for your email address and then send a token to that adress. You should copy paste that token into the private chat with the bot who then provides you the role (student per default). The role assigned upon verification can be changed by typing "$verify_tutors" or "$verify_students". This state is not saved when the bot goes offline in between. The database persists also when the bot goes offline. Verifying multiple times with the same email address is not possible. Basic SQL injections should be prohibited.

The bot can be personalized by adjusting the texts it sends and the required email address. You can for instance ask for an address with a specific ending, see security.py
