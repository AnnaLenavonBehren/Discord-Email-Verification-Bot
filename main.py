# This example requires the 'message_content' intent.
import os
import discord
from dotenv import load_dotenv
from send_email import send_verification_email_to
from data import create_entry, create_database, add_email, get_token, verify, update_roles, email_occupied, remove_entry
import asyncio
import re
from security import valid_email
from discord.ext import commands
import sqlite3
from sqlite3 import Error

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    global verification_role, guild, ver_channel, public_channel, auth_channel, admin, tutor, student, not_verified, db
    global ADMIN_ID, GUILD_ID, TUTOR_ID, STUDENT_ID, NOT_VERIFIED_ID, PUBLIC_CHANNEL_ID, AUTH_CHANNEL_ID, VER_CHANNEL_ID

    # load private data from .env file
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
    GUILD_ID = int(os.getenv('GUILD_ID'))
    TUTOR_ID = int(os.getenv('TUTOR_ID'))
    STUDENT_ID = int(os.getenv('STUDENT_ID'))
    NOT_VERIFIED_ID = int(os.getenv('NOT_VERIFIED_ID'))
    PUBLIC_CHANNEL_ID = int(os.getenv('PUBLIC_CHANNEL_ID'))
    AUTH_CHANNEL_ID = int(os.getenv('AUTH_CHANNEL_ID'))
    VER_CHANNEL_ID = int(os.getenv('VER_CHANNEL_ID'))
    db = os.getenv('DB')

    # set global variables
    guild = client.get_guild(GUILD_ID)
    public_channel = client.get_channel(PUBLIC_CHANNEL_ID)
    auth_channel = client.get_channel(AUTH_CHANNEL_ID)
    ver_channel = client.get_channel(VER_CHANNEL_ID)
    admin = guild.get_role(ADMIN_ID)
    tutor = guild.get_role(TUTOR_ID)
    student = guild.get_role(STUDENT_ID)
    verification_role = guild.get_role(STUDENT_ID)
    not_verified = guild.get_role(NOT_VERIFIED_ID)
    
    # create initial database
    create_database(db)
    print('Initial database created')



@client.event
async def on_member_join(member):
    await member.send("Welcome to this discord server!!")
       
    await verification(member)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global verification_role
    dm_channel = (message.channel.type == isinstance(message.channel, discord.DMChannel))
    verify = (message.content == "verify")
    
    if verify:
        member = guild.get_member(message.author.id)
        await verification(member)

    if (message.channel.id == VER_CHANNEL_ID):
        print("Now in ver channel")
        if message.content == "$verify_tutors":
            verification_role = tutor
            print("verifying tutors")
            await ver_channel.send("Now verifying tutors.")
        if message.content == "$verify_students":
            verification_role = student
            print("verifying students")
            await ver_channel.send("Now verifying students.")



async def verification(member):
    
    USER_ID = member.id

    try:
        
        roles = member.roles

        await member.remove_roles(student)
        await member.remove_roles(tutor)
        await member.add_roles(not_verified)
        
        remove_entry(db, member)

        # Welcome message
        await member.send('To verify yourself on this server, enter your e-mail address.')
        
        def check_email(m):
            return m.author == member and re.match(r"[^@]+@[^@]+\.[^@]+", m.content) and isinstance(m.channel, discord.DMChannel)

        try:
            email_msg = await client.wait_for("message", check=check_email, timeout=600)

        except asyncio.TimeoutError:
            await auth_channel.send(f"<@&{ADMIN_ID}>" +"**"+ str(member.name) + "** with id " + f"<{USER_ID}>" + " timed out.")
            await member.send("The time limit for verification has been exceeded. Please write `verify` in the chat to restart the verification.")
            return

        email = email_msg.content.strip().lower()

        
        if email_occupied(db, email):
            await member.send("This e-mail address is already being used by another account. If this is not yours, please contact an administrator.")
            return

        if not valid_email(email):
            await member.send("Invalid e-mail address. Please restart the verification process by entering `verify`.")
            return

        create_entry(db, member)
        add_email(db, member, email)
        true_token = get_token(db, member)
        send_verification_email_to(email, true_token)
        
        
        await member.send("An e-mail with a verification token should arrive in your mailbox shortly. Please reply to this message using this token only.")

       
        # Token Eingabe
        def check_token(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        try:
            token_msg = await client.wait_for("message", check=check_token, timeout=600)
            input_token = token_msg.content
            correct_token = (input_token == true_token)

            if correct_token:
                await member.remove_roles(not_verified)
                await member.add_roles(verification_role)
                verify(db, member, verification_role.name)
                await member.send('The verification was successful. You now have access to the private area of this server. If this is not the case, please contact an admin of the server.')
                
            else:
                await member.send('Wrong token. Please restart the verification by entering `verify`.')
                await auth_channel.send(f"<@&{ADMIN_ID}>" +"**"+ str(member.name) + "** with id " + f"<{USER_ID}>" + " sent a wrong token.")

        except asyncio.TimeoutError:
            await auth_channel.send(f"<@&{ADMIN_ID}>" +"**"+ str(member.name) + "** with id " + f"<{USER_ID}>" + " timed out.")
            await member.send("The time limit for verification has been exceeded. Please write `verify` in the chat to restart the verification.")
            return

        
    except discord.Forbidden:
        
        await public_channel.send(f"<@{USER_ID}>" + " Unfortunately, I cannot send you a private message. This is probably because you have disabled **Allow direct messages from server members** in your account's privacy settings. Please allow this temporarily and join the server again to restart the verification or contact an admin.")
        await auth_channel.send(f"<@&{ADMIN_ID}>" + " Could not write private message to **" + str(member.name) + "** with id " + f"<{USER_ID}>")


@client.event
async def on_member_update(before, after):
    # update role
    if before.roles != after.roles:
        update_roles(db, after)


client.run(os.getenv('TOKEN'))
