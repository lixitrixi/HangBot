# Imports
import discord
from discord.ext import commands
import nltk
from nltk.corpus import words
from math import log
import random as r
r.seed()

client=commands.Bot(command_prefix='_')

Token = 'Njg3Nzg2NTc3MTc0MjAwMzYw.Xmq1Pg.vVnlLvROf0l1v-22SukYvJbnfUQ'

client.remove_command('help') #a custom help command is made later

# Variables
client.data = {} # {Guild id: [channel id, message id, [user1, user2], word, tries, guess history]}

# Functions
def mask(hist, word): #returns a word showing only letters that have been guessed
    return_word = []

    for i in word:
        if i in hist:
            return_word.append(i)
        else:
            return_word.append('█')
    
    return return_word

def checkValidity(message):
    if message.author.id != 687786577174200360 and\
    isletter(message.content) and\
    message.guild.id in client.data and\
    message.channel.id == client.data[message.guild.id][0] and\
    message.author.id in client.data[message.guild.id][2]:
        return True
    else:
        return False

def isletter(i): #checks if input is a single letter
    if i.isalpha() and len(i)==1:
        return True
    else:
        return False

async def processGuess(message):
    data = client.data[message.guild.id]

    result = '' #the message that will be displayed to the user

    play_menu = await message.channel.fetch_message(data[1])

    if message.content.lower() in data[5]: #guess has already been made
        result = "has already been guessed!"

    elif message.content.lower() in data[3]: #guess is correct
        data[5].append(message.content.lower()) #adds guess to history
        result = "is correct!"

    else: #guess is incorrect
        data[5].append(message.content.lower()) #adds guess to history
        data[4] -= 1 #takes away one try
        result = "is incorrect!"

    await message.channel.purge(limit=1)

    if ''.join(mask(data[5], data[3])).isalpha(): #checks if the whole word has been guessed
        await play_menu.edit(content="{0} is correct!\nYou guessed the word: {1}\nUse '_new' to start a new game.".format(message.content.lower(), ''.join(data[3])))
        data[1] = 0 #sets the channel id to 0 to negate any future guesses

    elif data[4] < 1: #checks if there are no tries remaining
        await play_menu.edit(content="Game over!\nThe word was: {0}\n Use '_new' to start a new game.".format(''.join(data[3])))
        data[1] = 0

    else:
        await play_menu.edit(content="**{0}** {1}\n{2}\nTries: **{3}**\nGuesses: {4}".format(message.content.lower(), result, ' '.join(mask(data[5], data[3])), data[4], ' | '.join(data[5])))
        #edits the play menu to display the result of the guess, the masked word, and remaining tries

    client.data[message.guild.id] = data #updates client.data with results of the guess

# Embeds
help_menu = discord.Embed(
    title = 'Help',
    colour = discord.Colour.green())
help_menu.add_field(name='_ping', value='Displays the latency of the bot', inline=False)
help_menu.add_field(name='_invite', value="Responds with the bot's invite link", inline=False)
help_menu.add_field(name='_new', value='Starts a new game of hangman', inline=False)
help_menu.add_field(name='_join', value='Lets you join the current game in your server', inline=False)
help_menu.add_field(name='How to play:', value='After starting a game or joining an existing one, simply send letters to the channel that the display is in.')

# Events
@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message):
    if checkValidity(message):
        await processGuess(message)

    await client.process_commands(message)


# Commands
@client.command(aliases=['h'])
async def help(ctx):
    await ctx.send(embed=help_menu)

@client.command() #responds with the bot's invite link
async def invite(ctx):
    await ctx.send("Here's my invite link!\nhttps://discordapp.com/api/oauth2/authorize?client_id=687786577174200360&permissions=8&scope=bot")

@client.command() #responds with the bot's latency in the ctx channel
async def ping(ctx):
    await ctx.send(f'Pong! ({round(client.latency*1000)}ms)')

@client.command()
async def join(ctx):
    if ctx.guild.id in client.data and ctx.message.author not in client.data[ctx.guild.id][2]:
        client.data[ctx.guild.id][2].append(ctx.message.author.id)
    
    await ctx.channel.purge(limit=1)

@client.command()
async def new(ctx):
    if isinstance(ctx.channel, discord.abc.GuildChannel):
        word = list(r.choice(words.words()).lower()) #chooses a random word and turns it into a list of letters
        data = [ctx.channel.id, 0, [ctx.author.id], word, round(1.2*log(len(word), 1.5))+2, []] #makes an entry to add to client.data

        await ctx.send(f"Here's a new word!\n{' '.join(mask([], word))}\nTries: **{data[4]}**") #sends the formatted word

        async for message in ctx.channel.history(limit=5): #finds the play menu that was just sent and records its ID in the client.data entry
            if message.author.id == 687786577174200360:
                data[1] = message.id
                break

        client.data[ctx.guild.id] = data #adds or updates entry in client.data

        print(''.join(word))


# Runtime
client.run(Token)
