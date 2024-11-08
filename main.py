import os

import random

import re

import time

import asyncio


import discord

# Bot token

token = os.environ['token']


# Setup intents

intents = discord.Intents.default()

intents.message_content = True

intents.reactions = True

client = discord.Client(intents=intents)


# Global variables

url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

cooldowns = {}

cooldown_duration = 60 * 60

points = {}  # Dictionary to store points for each user

bot_messages = {}

stored_messages = {}  # To store messages along with like count and user ID

feedback_cooldowns = {}

feedback_cooldown_duration = 7 * 24 * 60 * 60

feedback_channel = int(os.environ['feedbackchannel'])

announcement_channel = int(os.environ['announcement_channel'])

stock_channel = int(os.environ['stock_channel'])

bank = {}

vbank = {}

reset_duration =  90 * 24 * 60 * 60

next_reset_time = time.time() + reset_duration

ana_points = random.randint(10000, 20000)

bot_id = 1279425767457165312

patterns = [
    re.compile(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b'),  # Phone numbers
    re.compile(r'\b\d{5}[-.\s]??\d{6}\b'),  # International phone numbers
    re.compile(r'@[a-zA-Z0-9._]+'),  # Social media handles
    re.compile(r'(https?://[^\s]+)'),  # URLs
    re.compile(r'\b\d{4}[-.\s]??\d{4}[-.\s]??\d{4}[-.\s]??\d{4}\b'),  # Credit card numbers
    re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),  # Emails
    re.compile(r'\b[A-Za-z0-9._]+#[0-9]{4}\b'),  # Discord tags
    re.compile(r'(fb|ig|insta|snap|sc):?\s?@[A-Za-z0-9._]+'),  # Social media shorthand
    re.compile(r'(ssn|social security):?\s?\d{3}[-.\s]?\d{2}[-.\s]?\d{4}'),  # SSN patterns
    re.compile(r'(passport|id number):?\s?[A-Za-z0-9]+'),  # ID/passport numbers
    re.compile(r'(venmo|cashapp|paypal|btc):?\s?@[A-Za-z0-9._]+'),  # Payment service IDs
    re.compile(r'(dl|driver\'s license):?\s?\d+'),  # Driver's license number
    re.compile(r'(account number|routing number):?\s?\d{9,12}'),  # Bank account/routing numbers
    re.compile(r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'),  # U.S. Social Security Number
    re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),  # IPv4 addresses
    re.compile(r'\b\d{1,5}\s+\w+\s+\w+,\s+\w+\s+\d{5}\b'),  # U.S. address format
    re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/(19|20)?\d{2}\b'),  # Date of birth (MM/DD/YYYY)
]



# Event listener for when the bot has connected to Discord

@client.event

async def on_ready():
    
    print(f'We have logged in as {client.user}')

    client.loop.create_task(timer_start())

    client.loop.create_task(clean_old_messages())

    client.loop.create_task(stock_announcements())

    await client.wait_until_ready()

    if bot_id not in points:

        points[bot_id] = ana_points




# Sort users by points

def get_leaderboard():
    
    sorted_points = sorted(
        
        [(user, score) for user, score in points.items() if user != client.user.id],
        
        key=lambda x: x[1], reverse=True
        
    )
    
    return sorted_points




async def ana_lb(message):
    
    if message.content.lower() == 'ana lb':
        
        leaderboard = get_leaderboard()
        
        user_id = message.author.id
        
        
        # Prepare leaderboard message
        
        leaderboard_message = "**Leaderboard:**\n"
        
        for idx, (user, score) in enumerate(leaderboard[:10]):
            
            username = await client.fetch_user(user)  # Get the username for user ID
            
            leaderboard_message += f"{idx + 1}. **{username.name}** - **{score}** points\n"
            

        # Find personal position
        
        personal_position = next((idx + 1 for idx, (user, score) in enumerate(leaderboard) if user == user_id), None)
        
        if personal_position:
            
            leaderboard_message += f"\nYou are currently in position **{personal_position}** with **{points[user_id]}** points."
            
        else:
            
            leaderboard_message += "\nYou are not in the leaderboard yet."

        await message.channel.send(leaderboard_message)




async def ana_hlw(message):
    
    if message.content.lower() == 'ana hlw':
        
        await message.channel.send('Hi! I am **Ana-chan**, and Ana stands for Anarchy! But you can call me **Ana** though. If you need any help, just ask me by saying **"ana hlp"**. I will be more than happy to help you!')




async def ana_hlp(message):
    
    if message.content.lower() == 'ana hlp':
        
        await message.channel.send( '''
Heres a list of commands you can use:
- **ana hlw**: Say hi to me!
- **ana hlp**: Shows this message.
- **ana des**: Know more about me and my job as a virtual anonymous mailwoman!
- **ana msg**: Type a message after writing this command and I will help you voice you message to the world!(This command can be used once every **60 minutes**)
- **ana giv**: See what an anonymous voice of the world has to say! 
- **ana showpts**: See how many points you have!
- **ana feedback**: Give you feedback or what you would like to see be added to the bot!(WARINING: We, the developers can see who and what the user sends if one uses this command, so unnecessary texts are advisable not to send. This command can be used once every **7 days**)
- **ana cldwn**: Shows cooldowns for commands.
- **ana lb**: Shows the leaderboard of points.
- **ana buy bank**: Buy a bank account to store the Ana currency, Archs! You need **1000** points to buy a bank account. You can only have 1 bank account.
- **ana bank**: Shows how much Archs you bank account have.
- **ana conv**: Convert points to Archs. This process is irreversible with and exchange rate of **10 points = 1 Arch**.
- **ana retimer**: Shows the time remaining for the next reset.
- **ana buy vbank**: Buy a virtual bank account to store the variable currency, Anas.
- **ana vbank**: Shows how much Anas you have in your vbank account.
- **ana stock**: Shows the current exchange rate of Anas.
- **ana bs**: Buy stock with this command.
- **ana ss**: Sell stock with this command.
- **ana shop**: Shows the shop.''')
        




async def ana_des(message):
    
    if message.content.lower() == 'ana des':
        
        await message.channel.send('Do you feel like your **voice is not loud enough for the world to hear**? Do you want your journals to be **read by the world**? Do you want to share the **deepest darkest secrets**? Or do you want to take the load off your chest by **confessing your love anonymously to the world**? You can do it here, right now! Using your trusted **AnaChan**! The **anonymous virtual mailwoman**!')




async def ana_msg(message):
    
    if message.content.lower().startswith('ana msg'):
        
        user_id = message.author.id
        

        # Check for cooldown
        
        if user_id in cooldowns and cooldowns[user_id] > time.time():
            
            remaining_time = cooldowns[user_id] - time.time()
            
            minutes, seconds = divmod(remaining_time, 60)
            
            await message.channel.send(f"Please wait **{int(minutes)}** minutes and **{int(seconds)}** seconds before using this command again.")
            
            return
            
           
        # Get the user's message after 'Ana msg '
        
        user_message = message.content[8:]
        

        # Check if the message contains a URL
        
        for pattern in patterns:
            
            if pattern.search(user_message):
                
                await message.channel.send('Personal information is not allowed in the message.')
                
                return
            

        # Store the message, with initial like count of 0 and the user ID
        
        stored_messages[user_message] = {
            
            "like_count": 0,
            
            "user_id": user_id,

            "time": time.time()
            
        }

        await message.channel.send(f'Your message: **{user_message}** has been saved for the world to see.')
        
        cooldowns[user_id] = time.time() + cooldown_duration




async def ana_giv(message):
    
    if message.content.lower() == 'ana giv':
        
        if stored_messages:
            
            # Get a random message and its details
            
            random_message = random.choice(list(stored_messages.keys()))
            
            like_count = stored_messages[random_message]["like_count"]
            
            original_author_id = stored_messages[random_message]["user_id"]
            

            # Send the random message
            
            response_message = await message.channel.send(f"Here's a voice of a random person: **{random_message}**")
            
            await response_message.add_reaction('👍')
            

            # Store the bot's message ID and map it to the original message content
            
            bot_messages[response_message.id] = random_message
            

            # Display the like count
            
            await message.channel.send(f'This message has {like_count} likes.')
            
        else:
            
            await message.channel.send('No messages available yet. Use **"ana msg"** to save a message!')
            



async def ana_showpts(message):
    
    if message.content.lower() == 'ana showpts':
        
        user_id = message.author.id
        
        if user_id in points:
            
            await message.channel.send(f'You have {points[user_id]} points!')
            
        else:
            
            await message.channel.send('You have not earned any points yet.')
            



async def ana_feedback(message):
    
    if message.content.lower().startswith('ana feedback'):
        
        user_id = message.author.id
        
        if user_id in feedback_cooldowns and feedback_cooldowns[user_id] > time.time():
            
            remaining_time = feedback_cooldowns[user_id] - time.time()
            
            days_feedback, rem_time_feedback = divmod(remaining_time, 24 * 60 * 60)
            
            days, minutes = divmod(rem_time_feedback, 60 * 60)
            
            await message.channel.send(f'Please wait **{int(days)}** days and **{int(minutes)}** minutes before using this command again.')
            
            return

        
        feedback = message.content[13:]
        
        feedbackchannel = client.get_channel(feedback_channel)
        
        if isinstance(feedbackchannel, discord.TextChannel):  # Check if it's a text channel
            
            await feedbackchannel.send(f'Feedback from **{message.author}**: **{feedback}**')
            
        await message.channel.send('Thank you for your feedback, we will work into it.')
        
        feedback_cooldowns[user_id] = time.time() + feedback_cooldown_duration



async def ana_cldwn(message):
    
    if message.content.lower() == 'ana cldwn':
        
        user_id = message.author.id
        

        # Check cooldown for "ana msg"
        
        if user_id in cooldowns and cooldowns[user_id] > time.time():
            
            remaining_time_msg = cooldowns[user_id] - time.time()
            
            minutes_msg, seconds_msg = divmod(remaining_time_msg, 60)
            
            cooldown_msg = f"**Ana msg**: {int(minutes_msg)} minutes and {int(seconds_msg)} seconds left."
            
        else:
            
            cooldown_msg = "**Ana msg**: No cooldown. You can use this command."
            

        # Check cooldown for "ana feedback"
        
        if user_id in feedback_cooldowns and feedback_cooldowns[user_id] > time.time():
            
            remaining_time_feedback = feedback_cooldowns[user_id] - time.time()
            
            days_feedback, rem_time_feedback = divmod(remaining_time_feedback, 24 * 60 * 60)
            
            hours_feedback, minutes_feedback = divmod(rem_time_feedback, 60 * 60)
            
            cooldown_feedback = f"**Ana feedback**: {int(days_feedback)} days, {int(hours_feedback)} hours left."
            
        else:
            
            cooldown_feedback = "**Ana feedback**: No cooldown. You can use this command."
            

        # Send the cooldown statuses
        
        await message.channel.send(f"{cooldown_msg}\n{cooldown_feedback}")



async def ana_buy_bank(message):

    if message.content.lower() == 'ana buy bank':
        
        user_id = message.author.id

        if user_id not in bank:
            
            if user_id in points and points[user_id] >= 1000:
                
                points[user_id] -= 1000
                
                bank[user_id] = 10
                
                await message.channel.send('You have successfully created a bank account.')

                
            else:
                
                await message.channel.send('You do not have enough points to create a bank account.')

                
        else:
            
            await message.channel.send('You already have a bank account.')



async def ana_conv(message):
    
    if message.content.lower().startswith('ana conv'):
        
        user_id = message.author.id
        
        amount = int(message.content[8:])
        
        if user_id in points and user_id in bank and amount > 0 and points[user_id] >= amount:
            
            points[user_id] -= amount
            
            bank[user_id] += amount/10
            
            await message.channel.send(f'You have successfully converted **{amount}** points to **{amount/10}** Archs.')
            

        else:
            
            await message.channel.send('You dont have enough points or you dont have a bank account or you inserted negative points.')





async def ana_bank(message):
    
    if message.content.lower() == 'ana bank':
        
        user_id = message.author.id
        
        if user_id in bank:
            
            await message.channel.send(f'You have **{bank[user_id]}** Archs in your bank account.')
            

        else:
            
            await message.channel.send('You dont have a bank account.')




async def creator(message):
    
    creator_id = int(os.environ['readkey'])
    
    if message.author.id == creator_id:
        
        await creator_command(message)




async def creator_command(message):
    
    if message.content.lower().startswith('ana givpts'):
        
        pts = int(message.content[11:])
        
        creator_id = int(os.environ['readkey'])
        
        if creator_id in points:
            
            points[creator_id] += pts

        
        else:
            
            points[creator_id] = pts

        await message.channel.send(f'Successfully given **{pts}** points to the creator, ReadKey.')




async def timer_start():
    
    while True:

        global ana_points
        
        await asyncio.sleep(reset_duration)
        
        await timer()

        ana_points = random.randint(10000, 20000)

        points[bot_id] += ana_points
        



async def timer():
    
    global next_reset_time, points
    
    for user_id in points:
        
        points[user_id] = 0
        
        announcementchannel = client.get_channel(announcement_channel)
        
        if isinstance(announcementchannel, discord.TextChannel):
            
            await announcementchannel.send("**Points have been reset for all users.**")
            
        
    next_reset_time = time.time() + reset_duration




async def retimer(message):
    
    if message.content.lower() == 'ana retimer':
        
        remaining_time = next_reset_time - time.time()
        
        if remaining_time > 0:
            
            days, rem_sec = divmod(remaining_time, 24 * 60 * 60)
            
            hours, min_sec = divmod(rem_sec, 60 * 60)
            
            minutes, seconds = divmod(min_sec, 60)
            
            await message.channel.send(f'The next reset will be in **{int(days)}** days, **{int(hours)}** hours, **{int(minutes)}** minutes, and **{int(seconds)}** seconds.')

        
        else:
            
            await message.channel.send("Reset has already been complete.")




async def stock_market(message):
    
    total_points = sum(points.values())
    
    #exchange rate / value of one ana
    
    exchange_rate = total_points / ana_points
    
    if message.content.lower() == 'ana stock':
        
        await message.channel.send(f'The current exchange rate is: 1 Ana = **{exchange_rate}** Points.')


async def ana_bs(message):
    
    if message.content.lower().startswith('ana bs'):
        
        user_id = message.author.id
        
        total_points = sum(points.values())
        
        exchange_rate = total_points / ana_points
        
        amount = int(message.content[6:])
        
        ana_price = exchange_rate * amount
        
        if amount <= 0:
            
            await message.channel.send("Stocks cannot be negative.")
            
            return

        
        if user_id in points and user_id in vbank and points[user_id] >= ana_price:
            
            points[user_id] -= ana_price
            
            vbank[user_id] += amount
            
            await message.channel.send(f'You have successfully bought **{amount}** Anas for **{ana_price}** points with an exchange rate of **{exchange_rate}**')

        
        else:
            
            await message.channel.send("You do not have enough points or you dont have a bank account.")



async def ana_ss(message):
    
    if message.content.lower().startswith('ana ss'):
        
        user_id = message.author.id
        
        total_points = sum(points.values())
        
        exchange_rate = total_points / ana_points
        
        amount = int(message.content[6:])
        
        ana_price = exchange_rate * amount
        
        if amount <= 0:
            
            await message.channel.send("Prices cannot be negative.")
            
            return
            

        if user_id in points and user_id in vbank and vbank[user_id] >= amount:
                
            vbank[user_id] -= amount
                
            points[user_id] += ana_price
                
            await message.channel.send(f'You have successfully sold **{amount}** Anas for **{ana_price}** points with an exchange rate of **{exchange_rate}**')

            
        else:
                
            await message.channel.send("You do not have enough Anas in your vbank account.")

        
        
async def ana_buy_vbank(message):
    
    if message.content.lower() == 'ana buy vbank':
        
        user_id = message.author.id
        
        if user_id in vbank:
            
            await message.channel.send('You already have a vbank account.')
            
            return
            

        if user_id in bank and bank[user_id] >= 100:
            
            bank[user_id] -= 100
            
            vbank[user_id] = 0
            
            await message.channel.send('You have successfully created a vbank account.')
            

        else:
            
            await message.channel.send('You dont have enough Archs in you bank account.')




async def ana_vbank(message):
    
    if message.content.lower() == 'ana vbank':
        
        user_id = message.author.id

        if user_id in vbank:
        
            await message.channel.send(f'You have **{vbank[user_id]}** Anas in your vbank account.')

        
        else:
            
            await message.channel.send("You dont have a vbank account.")


async def clean_old_messages():
    
    while True:
        
        current_time = time.time()
        
        for user_message, data in list(stored_messages.items()):
            
            if current_time - data["time"] >= 30 * 24 * 60 * 60:
                
                del stored_messages[user_message]
                
        
        await asyncio.sleep(24 * 60 * 60)




async def ana_shop(message):
    
    if message.content.lower() == 'ana shop':
        
        await message.channel.send("**Ana's Shop:**\n\n1. Buy Ana Bank: **100 Points**; Use command **Ana buy bank**\n2. Buy Ana Vbank: **100 Archs**; Use command **Ana buy vbank**")



async def stock_announcements():
    
    stockchannel = client.get_channel(stock_channel)
    
    while True:
        
        total_points = sum(points.values())
        
        exchange_rate = total_points / ana_points
        
        if isinstance(stockchannel, discord.TextChannel):
            
            await stockchannel.send(f'The current exchange rate is: 1 Ana = **{exchange_rate}** Points.')
            
        await asyncio.sleep(10)
        
        

    


# Event listener for when a message is received

@client.event

async def on_message(message):
    
    global stored_messages

    # Ignore messages sent by the bot itself
    
    if message.author == client.user:
        
        return

    await ana_hlw(message)

    await ana_hlp(message)

    await ana_des(message)

    await ana_lb(message)

    await ana_msg(message)

    await ana_giv(message)

    await ana_showpts(message)

    await ana_cldwn(message)

    await ana_feedback(message)

    await ana_buy_bank(message)

    await ana_buy_vbank(message)

    await ana_conv(message)

    await ana_bank(message)

    await creator(message)

    await retimer(message)

    await stock_market(message)

    await ana_vbank(message)

    await ana_shop(message)

    await ana_bs(message)

    await ana_ss(message)

    


# Event listener for reaction add

@client.event

async def on_reaction_add(reaction, user):
    
    # Check if the reaction is on a bot's message
    
    if reaction.message.id in bot_messages and str(reaction.emoji) == '👍':
        
        # Get the original message content
        
        message_content = bot_messages[reaction.message.id]
        
        # Increment the like count
        
        stored_messages[message_content]["like_count"] += 1
        

            # Get the user ID of the original author
        
        original_author_id = stored_messages[message_content]["user_id"]
        

            # Award the original author 10 points
        
        if original_author_id in points:
            
            points[original_author_id] += 10
            
        else:
            
            points[original_author_id] = 10
            




    

# Event listener for reaction remove
    
@client.event

async def on_raw_reaction_remove(payload):
    
    # Check if the reaction is on a bot's message and if it's a 👍 reaction
    
    if payload.message_id in bot_messages and str(payload.emoji) == '👍':
        
        message_content = bot_messages[payload.message_id]
        
        # Decrement the like count but ensure it doesn't go below 0
        
        stored_messages[message_content]["like_count"] = max(stored_messages[message_content]["like_count"] - 1, 0)
        

        # Get the user ID of the original author
        
        original_author_id = stored_messages[message_content]["user_id"]
        

        # Deduct 10 points from the original author
        
        if original_author_id in points:
            
            points[original_author_id] = max(points[original_author_id] - 10, 0)
            






# Running the bot

client.run(token)
