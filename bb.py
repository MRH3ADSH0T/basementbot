# The Basement Bot
# Documentation:    https://discordpy.readthedocs.io/en/latest/api.html
# Event reference:  https://discordpy.readthedocs.io/en/latest/api.html?highlight=role%20mention#event-reference

from timeit import default_timer as dt
st=dt() # start of all code

#import warnings
#warnings.filterwarnings("ignore")

# discord-oriented tools
import discord
from discord.ext import commands
import json
import asyncio as aio
from discord_slash import SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
# system
from sys import getsizeof
from os.path import isfile, dirname, getsize, getmtime
from contextlib import redirect_stdout
from dotenv import dotenv_values as dev
from os import system
# time
from datetime import datetime as datet
from pytz import timezone
import time
# misc.
import random as rand
from hashlib import sha256 as sha
from io import StringIO
#from profanity_filter import ProfanityFilter
#from profanity_check import predict as pf_predict

BOOT_TIME=datet.now().strftime("%m/%d/%Y %H:%M:%S")

# initialize discord API
client=commands.Bot(
    command_prefix="",
    intents=discord.Intents.all(),
    max_messages=1024,
    owner_id=483000308876967937 # Me
)
slash=SlashCommand(client, sync_commands=True)
token=dict(dev(".env"))["bottoken"]

# profanity library init
#profanity_filter=ProfanityFilter()
#profanity_filter.censor_char="."

# current directory
client.dir=dirname(__file__)

GUILDS=[858065227722522644]
STAFF_ID=936734394591363182
DEPRECATED=[
    "setraw",
    "jd",
    "log",
    "test",
    "retrieve",
    "announce",
    "poll",
    "create",
    "stats", 
    "snow",
    "msgs",
    "del",
    "warn",
    "recent",
    "count",
    "dm",
    "sha"
]

ALIASES=DEPRECATED+[
    "clear",
    "snowflake",
    "statistics",
    "hash"
]

# user defined functions
def create(data:dict[int,dict[str,]], id_:int, name:str, time:str): # creates a member in the member data dictionary
    if id_ in data:
        return

    data[id_]={"name":f"{name}",
               "isMuted":False,
               "warnCount":0,
               "muteCount":0,
               "banCount":0,
               "msgCount":0,
               "permLvl":0,
               "countHigh":0,
               "countFails":0,
               "joinDate":time,
               "birthday":""}               

def save(dictionary): # saves member data in dictionary to hard storage
    direct=dirname(__file__)
    with open(f"{direct}/bb.json", "w") as f: json.dump(dictionary, f)

def load(): # loads member data
    with open(f"{client.dir}/bb.json", "r") as f: r=json.loads(f.read())
    new={int(i):r[i] for i in r if i.isdigit()}
    for i in r:
        if not i.isdigit(): new[i]=r[i]
    return new

def blSave(blist): # saves blacklisted words to hard storage
    direct=dirname(__file__)
    with open(f"{direct}/blw.txt", "w") as f:
        a="\n".join(i for i in blist)
        print(a, file=f)

def blLoad(): # loads blacklisted words
    with open(f"{dirname(__file__)}/blw.txt", "r") as f:
        return [i.strip() for i in f.readlines()]

def isListed(m,list_): return m.author in list_

def toDigits(num:str) -> list[int]:
    """
    Return a list of base-36 minus 10 converted string.
    For #alphabet-counting
    """
    return [-1]+[int(i,36)-10 for i in num]

def isNext(current:str,nextNum:str) -> bool:
    current, nextNum = current.lower(), nextNum.lower()
    if current==nextNum=="a":
        return True

    elif current[-1]=="z" and nextNum[-1]=="a":
        digcurrent, dignextNum=toDigits(current),toDigits(nextNum)
        return digcurrent[:-2]==dignextNum[:-2] and digcurrent[-2]+1==dignextNum[-2] or (current=="z"*len(current) and nextNum=="a"*len(nextNum) and len(current)==len(nextNum)-1)

    elif len(current)==len(nextNum):
        digcurrent, dignextNum=toDigits(current),toDigits(nextNum)
        return digcurrent[:-1]==dignextNum[:-1] and digcurrent[-1]+1==dignextNum[-1]

    else:
        return False

async def nickToMember(nick:str, author:discord.Member):
    memberGuesses:list[discord.Member]=[kiddie for kiddie in client.basement.members if kiddie.display_name.startswith(nick) or kiddie.name.startswith(nick)]
    if len(memberGuesses)==1:
        return memberGuesses[0]
    else:
        glist="\n"+"\n".join(kiddie.display_name for kiddie in memberGuesses)
        await client.modLog.send(f"{author.mention}, there are `{len(memberGuesses)}` people that match the username you provided me with (\"{nick}\") please check your spelling and/or specify further.{glist}")
        return

def verify(i:str):
    return i.strip() and not i.strip().startswith("#") and len(i.strip())-1

def parseDesciptions(cmd:str=None)->dict:
    "this was a ***** to code"
    if not cmd: cmds=["/"+cmd[1:] for cmd in dir(slashCmds) if not cmd.startswith("__")]
    else: cmds=[cmd]
    out={}

    with open(f"{client.dir}/bb.py",'r') as f:
        fread=[i.strip() for i in f.read().split("class slashCmds:")[-1].split('\n') if verify(i)]

    for command in cmds:
        for idx,line in enumerate(fread):
            if line.startswith("name=") and fread[idx-1]=="@slash.slash(" and line[6:-2]==command[1:]:
                name=command[1:]
                if fread[idx+1].startswith("description=f\""): desc=fread[idx+1][14:-2]
                else: desc=fread[idx+1][13:-2]
                out[name]=desc

    return out

def convertAttr(attr:str)->str:
    translations={
        "name":"Name",
        "isMuted":"Is muted?",
        "warnCount":"Warn count",
        "muteCount":"Mute count",
        "banCount":"Ban count",
        "msgCount":"Message count",
        "permLvl":"Permission level",
        "countHigh":"Highest count",
        "countFails":"Count fails",
        "joinDate":"Date joined",
        "birthday":"Birthday"
    }
    return translations[attr] if attr in translations else "INTERNALERROR"

def scanMessage(phrase:str, string:str) -> bool:
    phrase=phrase.lower()
    string=string.lower()
    chars=[".",",","-","‎"]
    try: percent=len([i for i in string if i==" "])/len(string)
    except ZeroDivisionError: percent=1
    for char in chars:
        if (phrase in string.replace(char,"").split(" ")):# and not phrase in string:
            return string.replace(char,"").replace(phrase, f"||{phrase}||")
    if phrase in string.replace(" ","") and not phrase in string and percent>.45:
        return string.replace(" ","").replace(phrase, f"||{phrase}||")
    elif f" {phrase} " in string or phrase==string:
        return string.replace(phrase, f"||{phrase}||")
    else:
        return False

# Grab our json/dictionary
client.Data=load()

####################################################################################################

@client.event
async def on_ready(): # do all this on startup...
    st=dt()
    client.basement=client.get_guild(858065227722522644) # basement guild
    client.botLog=client.basement.get_channel(862004853763866624) # bot log channel
    client.modLog=client.basement.get_channel(888981385585524766) # mod log channel
    client.counting=client.basement.get_channel(903043416571662356) # counting channel
    client.welcome=client.basement.get_channel(858065227722522647) # below are a list of channels
    client.checklist=client.basement.get_channel(862567884286984202)
    client.rules=client.basement.get_channel(858156716238438421)
    #client.group=client.basement.get_channel(871455541602430986) - channel deleted
    client.faq=client.basement.get_channel(858200405933555722)
    client.basementC=client.basement.get_channel(858157764530798612)
    client.wRole=client.basement.get_role(908491255812616252) # welcome role
    client.kRole=client.basement.get_role(858234453653848065) # kiddie role
    client.modRole=client.basement.get_role(858234453653848065) # moderator role
    client.adminRole=client.basement.get_role(858223675949842433) # admin role
    client.breakbbC=client.basement.get_channel(910345635365015613) # break-basementbot channel
    client.wrdAssocC=client.basement.get_channel(859807366219694080) # word association channel
    client.lSSC=client.basement.get_channel(933183879983013968) # newest minigame, long-story-short
    client.testC=client.basement.get_channel(933576021641400370) # test channel in dev category
    client.announcementC=client.basement.get_channel(858156757788524554)
    client.lastSave=dt() # used for autosaving
    client.localTZ=timezone("US/Central")
    print(f"Set up client variables in {dt()-st}s!")

    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time

    # repair files
    for channel in client.basement.channels:
        if not isfile(f"{client.dir}/logs/{channel.id}.txt"):
            with open(f"{client.dir}/logs/{channel.id}.txt", "w", encoding='utf-8') as f: print((f"BEGINNING OF #{channel.name}\n"), file=f) # if the channel log does not exist, create it

    for kiddie in [member for member in client.basement.members if not member.bot]: # in the case that data was corrupted, repair kiddie files
        if kiddie.id not in client.Data:
            create(client.Data, kiddie.id, kiddie.display_name, _dt)
            for role in kiddie.roles: # determine permission level for every kiddie
                if role.name=="Admin":
                    client.Data[kiddie.id]["permLvl"]=2
                    break
                elif role.name=="Mod":
                    client.Data[kiddie.id]["permLvl"]=1
                    break
            if kiddie.id==806307221171994624: client.Data[kiddie.id]["permLvl"]=3 # noah

        elif "joinDate" not in client.Data[kiddie.id]:
            print(f"Created joinDate entry for \"{kiddie.display_name}\"")
            joinDate:datet=kiddie.joined_at
            client.Data[kiddie.id]["joinDate"]=joinDate.astimezone(client.localTZ).strftime("%m/%d/%Y %H:%M:%S")

    # status
    notBots=[member for member in client.basement.members if not member.bot] # i don't know why, but the bot is always one less than the current count...
    await client.change_presence(activity=discord.Streaming(name=f"we've got {len(notBots)} members!",url="http://basement.minecraftr.us"))

    # sucess report
    await client.modLog.send(f"```{_dt} connected.```") # report connection
    hour, minute = client.Data["randTime"]
    print(f"Sucessfully loaded bot configurations! Startup took {dt()-st}s!\nGood-morning Time: {hour}:{minute}")

    # main loop
    while True:
        now=datet.now()
        if client.Data["GMday"]!=now.day and [now.hour,now.minute]==client.Data["randTime"]:
            await client.basementC.send(f"Good morning guys...")
            client.Data["GMday"]=now.day # reset day
            client.Data["randTime"]=[rand.randint(5,14),rand.randint(0,59)] # new random time
        
        if (now.hour,now.minute,now.second)==(12,0,0):
            for member in [i for i in client.Data if type(i)==int]:
                if client.Data[member]["birthday"]==_dt[:5]:
                    embed=discord.Embed(
                        title="HAPPY BIRTHDAY!",
                        description=f"Wishing <@{member}> a happy birthday! :tada:",
                        color=discord.Color.blue()
                    )
                    await client.basementC.send(embed=embed)
        
        if now.second==59 and now.minute==59 and now.hour==23 and now.day!=31 and now.month!=12: # will say "Goodnight, y'all" EXCEPT on new year's
            await client.basementC.send(f"Good night, y'all 😴")

        if now.minute==0 and 0<now.second<=10: # every hour (within a 10s error range), essentially execute "$log"
            online,o,dt_str="",0,now.strftime("%m/%d/%Y %H:%M:%S")
            for kiddie in client.basement.members:
                if kiddie.raw_status!="offline" and kiddie.bot==False:
                    online+=" - "+kiddie.display_name+"\n"
                    o+=1
            await client.modLog.send(f"This was an auto-initiated process. Use `/log` to see this list.\n{o} online members at `{dt_str}`:```\n{online}```") # send to #modlogging
            await aio.sleep(10)

        if now.minute==59 and now.hour==23 and now.day==31 and now.month==12:
            if now.second==0:
                await client.basementC.send("Get ready for the new year countdown!")
            cd=""
            if now.second>10:
                cd=f"***{60-now.second}***"
            else:
                cd=f"{60-now.second}"
            await client.basementC.send(cd)

        if now.second==0 and not now.minute%30:
            save(client.Data)

        await aio.sleep(1)

@client.event
async def on_member_join(member):

    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time

    if member.id!=864881059187130458 and member.id not in client.Data: # not Josh S. (alt)

        await client.welcome.send(f"{client.wRole.mention}, give a warm welcome to our newest member, {member.display_name}!") # public welcome

    elif member.id in client.Data:

        await client.welcome.send(f"{member.display_name} has returned!")

    if member.id==864881059187130458: # be funny bc alt
        await client.welcome.send(f"Yo <@864881059187130458> is here. Josh must be testing stuff again :man_shrugging:")

    # private DM
    await member.send(f"Dear, {member.mention}, thank you for joining **{client.basement.name}**! Please read the {client.checklist.mention} and {client.rules.mention} channels before exploring the server. Also, the Admin team loves to hear everyone's brilliant ideas, so using {client.faq.mention} is encouraged!\n\n        Sincerely, the Admin team")

    # give member childrne roll
    await member.add_roles(client.kRole)

    # create client.Data entry
    #client.Data[member.id]={"name":f"{member.name}",
    #                        "isMuted":False,
    #                        "warnCount":0,
    #                        "muteCount":0,
    #                        "banCount":0,
    #                        "msgCount":0,
    #                        "permLvl":0,
    #                        "countHigh":0,
    #                        "countFails":0,
    #                        "joinDate":None}
    create(client.Data, member.id, member.display_name, _dt)
    save(client.Data)

    # update member count
    notBots=[i for i in client.basement.members if not i.bot] # see on_ready()
    await client.change_presence(activity=discord.Streaming(name=f"we've got {len(notBots)} members!",url="http://basement.minecraftr.us"))

@client.event
async def on_member_remove(member):
    await client.welcome.send(f"{member.display_name} has left us... wishing them a happy life :)")
    notBots=[i for i in client.basement.members if not i.bot] # see on_ready()

    await client.change_presence(activity=discord.Streaming(name=f"we've got {len(notBots)} members!",url="http://basement.minecraftr.us"))

@client.event
async def on_member_update(before:discord.Member, after:discord.Member):
    now=datet.now()
    _dt=now.strftime("%m/%d/%Y %H:%M:%S") # get current time/date

    with open(f"{client.dir}/logs/nicknames.txt",'a', encoding="utf-8") as f:

        if before.display_name!=after.display_name:
            print(f"{_dt} {before.name} \"{before.display_name}\" -> \"{after.display_name}\"")

    with open(f"{client.dir}/logs/master.txt", "a", encoding="utf-8") as f:

        if before.status!=after.status and before.id!=691383407548301432: # change in status -- also dont include impersonator! creates clutter
            print(f"{_dt} {before.name} ({before.display_name})'s status was changed from \"{before.status}\" to \"{after.status}\"!", file=f)

        elif before.activity!=after.activity: # change in activity.... this is actually kinda creepy and a little bit intrusive
            print(f"{_dt} {before.name} ({before.display_name})'s activity was changed from {before.activity} to {after.activity}!", file=f)

        elif before.roles!=after.roles: # this is useful for identifying if that person was promoted or demoted
            # find out which role was changed
            bRoles,aRoles=[role.name for role in before.roles],[role.name for role in after.roles] # list of role names of before and after
            if len(bRoles)>len(aRoles): # find out which role was removed
                missing=str(list(set(bRoles)-set(aRoles))[0])
                print(f"{_dt} {before.name} ({before.display_name}) lost the role {missing}!", file=f)
                if missing in ["Admin","Mod"]: client.Data[before.id]["permLvl"]-=1 # if the role was important, subtract one... this is really quite clever actually
            if len(bRoles)<len(aRoles): # find out which role was added
                gained=str(list(set(aRoles)-set(bRoles))[0])
                print(f"{_dt} {before.name} ({before.display_name}) recieved the role {gained}!", file=f)
                if gained in ["Admin","Mod"]: client.Data[before.id]["permLvl"]+=1 # see line 113 comment

        elif before.pending!=after.pending: # no use for verification right now...
            print(f"{_dt} {before.name} ({before.display_name})'s verification was changed from {before.pending} to {after.pending}!", file=f)

@client.event
async def on_message_delete(message):
    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # get current time/date
    auth=message.author # author

    with open(f"{client.dir}/logs/{message.channel.id}.txt", "a", encoding="utf-8") as f:
        try:
            print(f"{_dt} {auth.name} ({auth.display_name})'s message was deleted \"{message.clean_content}\" in {message.channel.name}", file=f)
        except AttributeError:
            print(f"{_dt} {auth.name} ({auth.display_name})'s message was deleted \"{message.clean_content}\" in (probably) the DMs", file=f)

    if message.channel==client.counting and message.content.isdigit() and not message.content.startswith("0"): # counting alert
        await client.counting.send(f"{auth.name}'s message \"`{message.clean_content}`\" was deleted! The current number is `{client.Data['counting']}`")

@client.event
async def on_message_edit(before:discord.Message,after:discord.Message):
    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # get current time/date
    auth=before.author # author
    Bclean=before.clean_content # before
    Aclean=after.clean_content # after

    with open(f"{client.dir}/logs/{before.channel.id}.txt", "a",encoding="utf-8") as f:
        print(f"{_dt} {auth.name} ({auth.display_name}) changed their message from \"{Bclean}\" to \"{Aclean}\" (path: {before.channel.id}/{before.id})",file=f)

    if before.channel==client.counting and Bclean.isdigit(): # counting alert
        await before.reply(f"{auth.name} changed their message \"`{Bclean}`\")! The current number is `{client.Data['counting']}`",mention_author=False)
    
    # Profanity filter
    if profanity_filter.is_profane(Aclean):
        filtered=[]
        for word in Aclean.split(" "): filtered+=[f"||{word}||" if profanity_filter.is_profane(word) else word]
        await after.delete()
        await client.modLog.send(f"`{_dt}` {auth.display_name}'s message was deleted in {after.channel.mention}: \"{' '.join(filtered)}\"")

@client.event
async def on_raw_reaction_add(payload:discord.RawReactionActionEvent):
    emoji:discord.PartialEmoji=payload.emoji
    emojiAuth:discord.Member=client.get_user(payload.user_id)
    try: channel:discord.TextChannel=await client.fetch_channel(payload.channel_id)
    except: return
    message:discord.Message=await channel.fetch_message(payload.message_id)
    if payload.channel_id==858156662703128577: # polls channel

        message=await client.get_channel(858156662703128577).fetch_message(payload.message_id)

        if not emoji in (client.get_emoji(858556326548340746),client.get_emoji(858556294743064576)) and not message.author.bot:
            await message.remove_reaction(emoji,emojiAuth)

    #elif emoji==client.get_emoji(935571232173199380):
    #    channel:discord.TextChannel=client.get_channel(payload.channel_id)
    #    await channel.send("\"Based\"? Are you kidding me? I spent a decent portion of my life writing all of that and your response to me is \"Based\"? Are you so mentally handicapped that the only word you can comprehend is \"Based\" - or are you just some idiot who thinks that with such a short response, he can make a statement about how meaningless what was written was? Well, I'll have you know that what I wrote was NOT meaningless, in fact, I even had my written work proof-read by several professors of literature. Don't believe me? I doubt you would, and your response to this will probably be \"Based\" once again. Do I give a ****? No, does it look like I give even the slightest piece of anything about five fricking letters? I bet you took the time to type those five letters too, I bet you sat there and chuckled to yourself for 20 hearty seconds before pressing \"send\". You're so fricking pathetic. I'm honestly considering directing you to a psychiatrist, but I'm simply far too nice to do something like that. You, however, will go out of your way to make a fool out of someone by responding to a well-thought-out, intelligent, or humorous statement that probably took longer to write than you can last in bed with a chimpanzee. What do I have to say to you? Absolutely nothing. I couldn't be bothered to respond to such a worthless attempt at a response. Do you want \"Based\" on your gravestone?")

    if emoji==client.get_emoji(940789559829082212):
        await message.remove_reaction(emoji,emojiAuth)
        embed=discord.Embed(title="Red Flag!",description=f"{emojiAuth.mention} red flagged [this message]({message.jump_url})",color=discord.Color.red())
        await client.modLog.send(embed=embed)

@client.event
async def on_message(message:discord.Message):
    msg:str=message.content # get content (as opposed to the line below, content returns mentions and such)
    clean:str=message.clean_content # removes mentions and the like
    auth:discord.Member=message.author # get author
    _dt:str=datet.now().strftime("%m/%d/%Y %H:%M:%S") # get current time/date

    if auth==client.user or auth.bot: # prevent self or other bots from initiating basementbot interactions
        return
    # is muted check
    #if client.Data[auth.id]["isMuted"]:
    #    await message.delete() # delete the message, ofc
    #    await auth.send(f"You have been muted, please contact an Admin if you believe this is a mistake.") # notify the user
    #    try: channelName=message.channel.name
    #    except AttributeError: channelName="the DM"
    #
    #    with open(f"{client.dir}/logs/{message.channel.id}.txt", "a", encoding="utf-8") as f: # record the muted message, just in case ;)
    #        print(f"{_dt} {auth.name} ({auth.display_name}) ATTEMPTED to say \"{clean}\" in {channelName}", file=f)
    #    return

    # handle case reply for logging
    try:
        reply=message.reference
        if reply:
            rAuth:discord.Member=reply.resolved.author
            said=f"replied to {rAuth.display_name} ({reply.message_id}) with"
        else:
            said="said"
    except: said="replied to someone with"

    with open(f"{dirname(__file__)}/logs/{message.channel.id}.txt", "a", encoding="utf-8") as f: # record message. this is useful. very useful. i love data. lots of data
        print(f"{_dt} {auth.name} ({auth.display_name}) {said} \"{clean}\" (path: {message.channel.id}/{message.id})", file=f)

    if message.channel==client.testC:
        print(f"{_dt} {auth.display_name} - {msg}")
        #print(profanity_filter.extra_profane_word_dictionaries)

    #################################### blacklisted word check ####################################

    #if pf_predict([clean]) and "sick" not in clean.lower():
    #    filtered=[]
    #    for word in clean.split(" "): filtered+=[f"||{word}||" if profanity_filter.is_profane(word) else word]
    #    await message.delete()
    #    await client.modLog.send(f"`{_dt}` {auth.display_name}'s message was deleted in {message.channel.mention}: \"{' '.join(filtered)}\"")

    for word in client.Data["blw"]:
        filtered=scanMessage(word,clean)
        if filtered and (message.channel.id!=932125853003943956 and clean.lower()!="ass"):
            await message.delete()
            embed=discord.Embed(description=f"{auth.mention}'s message was deleted.\n\"{filtered}\"",color=discord.Color.red())
            await client.modLog.send(embed=embed)

    ################################################################################################

    if msg.startswith("$") and msg.split(" ")[0][1:] in ALIASES:
        await message.reply(f"`{msg.split(' ')[0]}` is deprecated. Please use the equivalent slash command.")
        return

    # create command needs to be before the permission assignment check below
    if msg.startswith("$create "):
        if client.Data[auth.id]["permLvl"]>1:
            new=message.mentions[0]
            create(client.Data, new.id, new.name)
            await message.channel.send(f"Sucessfully created memeber {new.display_name}, {auth.mention}!")
            await client.modLog.send(f"{new.name}'s new data:```py\n\"{new.id}\": {client.Data[new.id]}\n```")
        else:
            await message.channel.send(f"{auth.mention} make me. \*sticks out tounge*")

    # permission level; this is really quite clever, and uses some intuitive mathematics
    permL:int=client.Data[auth.id]["permLvl"]
    if len(message.mentions)>0: # extract mentions if any exist
        pred:list[discord.Member]=message.mentions
        predL=0
        if len(pred)==1: # if only one mention exists, treat it as a predicate and determine permission level
            if pred[0].id==437808476106784770: predL=0 # arcane bot
            elif pred[0].id==864192315576549388: predL=2 # basementbot's ID
            else: predL:int=client.Data[pred[0].id]["permLvl"]

        permL-=predL # the perm level will be 0 if the subject equals the predicate, negative if the predicate is superior, and positive if the subject is superior

    # +++++ fun +++++
    if clean.startswith("HAHA"):
        await message.delete()
        await message.channel.send(f"\*{auth.display_name}'s laugh was supressed by a pair of fancy acoustic pannels*")
    if msg.lower().replace(" ","")=="deadchat" or (msg.startswith("<:deadchat:906043591992934420>") and msg.endswith("<:deadchat:906043591992934420>")):
        await message.reply(file=discord.File(f"{client.dir}/static/sonic.png", filename="dontdownloadthis.png"), mention_author=False)
    if msg=="<@!864192315576549388>":#client.user.mention:
        print("triggered")
        await message.add_reaction("👋")

    #if msg.lower()=="based" or (msg.startswith("<:based:935571232173199380>") and msg.endswith("<:based:935571232173199380>")):
    #    await message.reply("\"Based\"? Are you kidding me? I spent a decent portion of my life writing all of that and your response to me is \"Based\"? Are you so mentally handicapped that the only word you can comprehend is \"Based\" - or are you just some idiot who thinks that with such a short response, he can make a statement about how meaningless what was written was? Well, I'll have you know that what I wrote was NOT meaningless, in fact, I even had my written work proof-read by several professors of literature. Don't believe me? I doubt you would, and your response to this will probably be \"Based\" once again. Do I give a ****? No, does it look like I give even the slightest piece of anything about five fricking letters? I bet you took the time to type those five letters too, I bet you sat there and chuckled to yourself for 20 hearty seconds before pressing \"send\". You're so fricking pathetic. I'm honestly considering directing you to a psychiatrist, but I'm simply far too nice to do something like that. You, however, will go out of your way to make a fool out of someone by responding to a well-thought-out, intelligent, or humorous statement that probably took longer to write than you can last in bed with a chimpanzee. What do I have to say to you? Absolutely nothing. I couldn't be bothered to respond to such a worthless attempt at a response. Do you want \"Based\" on your gravestone?")

    # +++++ Josh DMs +++++
    if message.channel.id==875194263267319808:
        if msg.startswith("$prank "):
            memberid=int(msg.split(" ")[1])
            kiddie=client.get_user(memberid)
            await client.welcome.send(f"{kiddie.display_name} has left us... wishing them a happy life :)")

    #if "cat" in msg and "girl" in msg and client.adminRole not in auth.roles:
    #    await message.delete()
    #    await client.modLog.send(f"```{_dt} {auth.display_name} ({auth.name}) said \"{msg}\"```")

    # +++++ counting +++++
    if message.channel.id==903043416571662356: # counting channel

        if clean.isdigit():
            # client.Data["counting"] is a 'discord.Message'. this allows access to both content and author
            if clean.startswith("0") and msg!="007":
                await message.delete()

            elif int(clean)==int(client.Data["counting"])+1 and client.Data["lastAuth"]!=auth.id:
                client.Data["counting"]=int(clean)
                client.Data["lastAuth"]=auth.id
                await message.add_reaction("✅")
                if int(clean)==100:
                    await message.add_reaction("💯")

                if int(clean)>client.Data[auth.id]["countHigh"]:
                    client.Data[auth.id]["countHigh"]=int(clean)

            else:
                if client.Data["counting"]>client.Data["high"]: # if this round beat the highscore
                    await message.channel.edit(name=f"🔢counting {client.Data['counting']}")
                    client.Data["high"]=client.Data["counting"]

                await message.add_reaction("🚳")
                client.Data["counting"]=0
                client.Data["lastAuth"]=0
                client.Data[auth.id]["countFails"]+=1
                cf=client.Data[auth.id]["countFails"]
                await message.channel.send(embed=discord.Embed(title="Count reset!",description=f"{auth.mention} reset the count! Their fail count: `{cf}`.\nThe count is now `0`. (The highscore is `{client.Data['high']}`)",color=discord.Color.red()))

        elif clean=="?":
            await message.delete()
            percent=round(client.Data["counting"]/client.Data["high"]*100,2)
            if client.Data["lastAuth"]!=0: last=client.basement.get_member(client.Data["lastAuth"]).mention
            else: last="**No one!**"
            info=discord.Embed(title=f"#counting info",color=discord.Color.blue())
            info.add_field(name="Current count",value=f"```{client.Data['counting']}```")
            info.add_field(name="Percent of highscore",value=f"```{percent}%```")
            info.add_field(name="Last counter",value=last,inline=False)
            await message.channel.send(embed=info)

        else: pass

    # +++++ alphabet counting +++++
    if message.channel.id==932125853003943956:
        last:list[discord.Message]=await message.channel.history(limit=10).flatten()
        last:discord.Message=[i for i in last[::-1] if not i.content.startswith("> ")][-2]

        if msg.startswith("> "): pass

        elif last.content.lower()==msg.lower()=="a":
            await message.add_reaction("✅")
        elif msg.isalpha() and isNext(last.content,msg.lower()) and auth!=last.author:
            await message.add_reaction("✅")
        else:
            await message.delete()

    # +++++ word-assoc +++++    

    # +++++ commands +++++

     ######## THE NEXT 2 COMMANDS ARE FOR LEGAL REASONS ########

    elif msg=="$records":
        await message.delete()
        print(f"{_dt} {auth.name} ({auth.display_name}) requested their records.")
        await auth.send(f"Per your request, here is all the data assigned to your discord ID in my database:```py\n{client.Data[auth.id]}\n```")
        return

    elif msg=="$erase":
        await message.channel.send(f"Are you sure you want to erase your Basement account? (You have 15 seconds to reply with \"confirm\")")

        def check(m): return m.author.id==auth.id and m.channel==message.channel and m.content=="confirm"

        try: await client.wait_for('message',check=check,timeout=20)

        except aio.TimeoutError: await message.channel.send(f"Task sucessfully failed.")

        else:
            client.Data[auth.id]={"name":f"{auth.name}",
                                  "isMuted":False,
                                  "warnCount":0,
                                  "muteCount":0,
                                  "banCount":0,
                                  "msgCount":0,
                                  "permLvl":0,
                                  "countHigh":0,
                                  "countFails":0,
                                  "joinDate":_dt}

            await auth.send(f"Data collected about you has been replaced to default values. If you would like to completely remove yourself from my database, you will need to leave {client.basement.name} and directly message Josh S. (Discord: MR_H3ADSH0T#0001)")
        return

    ############################################################

    elif msg.startswith("$inj") and message.channel==client.breakbbC:
        await client.breakbbC.send(f"Sorry, {auth.display_name}, but this command is currently disabled.")
        #return
        code,f=" ".join(i.strip() for i in clean.split(" ")[1:]),StringIO()

        if "input" in code or "import os" in code or "while True:" in code or "quit" in code:
            print(f"{_dt} - {auth.display_name} may be a troublemaker.")
            await message.channel.send(f"{auth.mention}, you may or may not have known that some of your code could break me, so I'm not gonna execute anything containing that")
            return
        try:
            with redirect_stdout(f): exec(code)
            out=f.getvalue()
            print(f"{_dt} - {auth.display_name} used '$inj'")
            await message.channel.send(f"{auth.mention}, I ran that python code and this is the output:```\n{out}\n```")
        except Exception as error:
            print(f"{_dt} - {auth.display_name} used '$inj' -- but it failed.")
            error=repr(error)
            await message.channel.send(f"{auth.mention}, I ran that python code and I encountered an error.```\n{error}\n```")
        return

    if message.channel.id not in [client.counting.id, client.modLog.id, client.botLog.id, client.wrdAssocC.id, client.lSSC.id] and not msg.startswith("/"):
        client.Data[auth.id]["msgCount"]+=1


####################################################################################################

class slashCmds:
    @slash.slash(
        name="jd", # /name <options>
        description="Looks up the join date of someone!",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="member",
                description="Whoever you want to look up. Leave blank to look up your own join date.",
                option_type=6, # User/member
                required=False
            )
        ]
    )
    async def _joindate(ctx:SlashContext,member:discord.Member=None):
        if not member: member=ctx.author
        embed=discord.Embed(title=member.display_name,color=member.color)
        embed.add_field(name="Join Date",value=f"```{client.Data[member.id]['joinDate']}```")

        await ctx.send(embed=embed)

    @slash.slash(
        name="howmanylines",
        description=f"How many lines long is BasementBot?",
        guild_ids=GUILDS
    )
    async def _howmanylines(ctx:SlashContext):
        lastMod=time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(getmtime(client.dir+"/bb.py")))
        with open("bb.py",'r') as f: lines=len(f.readlines())+1
        size=round(getsize("bb.py")/1024,2)
        embed=discord.Embed(title="Bot statistics",description="Visit <https://bot.thebasement.group> for more data!",color=discord.Color.blue())
        embed.add_field(name="Lines",value=f"```{lines}```")
        embed.add_field(name="Size",value=f"```{size}KB```")
        embed.add_field(name="Last edit",value=f"```{lastMod} CST```",inline=False)
        embed.add_field(name="Last boot time",value=f"```{BOOT_TIME}```",inline=False)
        await ctx.send(embed=embed)

    @slash.slash(
        name="dm",
        description="Directly messages a member and records it in #mod-logging.",
        guild_ids=GUILDS,
        default_permission=False,
        # two required options, the user and the message
        options=[
            create_option(
                name="member",
                description="The desired member to direct message.",
                option_type=6, # user
                required=True
            ),
            create_option(
                name="message",
                description="The message to send.",
                option_type=3, #string
                required=True
            )
        ]
    )
    # only @Staff can execute this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _dm(ctx:SlashContext,member:discord.Member,message:str):
        try:
            _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time
            # main command execution
            await member.send(f"Dear, {member.display_name},\n\n{message}\n\n\t\tSincerely, The Basement Staff Team")
            # log
            await client.modLog.send(f"```{_dt} - {ctx.author.display_name} messaged {member.display_name}:\n\"{message}\"```")
            # report success.
            await ctx.send(embed=discord.Embed(title="Success!",description=f"Sent {member.display_name} a direct message!",color=discord.Color.blue()))
        
        except discord.errors.Forbidden:    await ctx.send(embed=discord.Embed(title="Error!",description=f"Couldn't directly message {member.display_name}. Maybe they have \"accept direct messages\" off...",color=discord.Color.red()))
        except AttributeError:              await ctx.send(embed=discord.Embed(title="Error!",description=f"Were you trying to DM me? You can't DM me...",color=discord.Color.red()))

    @slash.slash(
        name="count",
        description="Sets the count to a specific number.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="new_number",
                description="Desired number.",
                option_type=4,
                required=True
            )
        ]
    )
    # Only @admins may use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=858223675949842433,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _count(ctx:SlashContext,new_number:int):
        client.Data["counting"]=new_number
        client.Data["lastAuth"]=ctx.author_id
        report=discord.Embed(title=f"Current number updated to `{new_number}`!",description=f"Anyone but {ctx.author.mention} can increase the count.",color=discord.Color.blue())
        await client.counting.send(embed=report)
        if ctx.channel!=client.counting: await ctx.send(embed=discord.Embed(title="Success!",color=discord.Color.blue()))

    @slash.slash(
        name="disconnect",
        description="Disconnects BasementBot.",
        guild_ids=GUILDS,
        default_permission=False
    )
    # Only @admins can execute this command.
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=858223675949842433,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _disconnect(ctx:SlashContext):
        _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time
        save(client.Data) # save data
        await client.modLog.send(f"```{_dt} {ctx.author.name} disconnected bot.```")
        await ctx.send(f"Disconnected.")
        print(f"{_dt} {ctx.author.name} initiated disconnect.")
        await client.close()

    @slash.slash(
        name="poll",
        description="Sends a poll out to everyone!",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="poll",
                description="The question",
                option_type=3,
                required=True
            )
        ]
    )
    # only @admins can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=858223675949842433,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _poll(ctx:SlashContext,poll:str):

        pollChannel=client.get_channel(858156662703128577)
        polled:discord.Message=await pollChannel.send(f"{client.kRole.mention}, "+poll)

        await polled.add_reaction(client.get_emoji(858556326548340746)) # upvote
        await polled.add_reaction(client.get_emoji(858556294743064576)) # downvote

        await ctx.send(f"Success!")

    @slash.slash(
        name="recent",
        description="Will fetch 50 most recent messages (including deleted messages) in the desired channel.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="channel",
                description="Which channel to grab messages from.",
                option_type=7, # channel
                required=True
            ),
            create_option(
                name="messages",
                description="Defaults to 50, you can increase or decrease this as much as you'd like",
                option_type=4, # integer
                required=False
            )
        ]
    )
    # only @staff can execute this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _recent(ctx:SlashContext,channel:discord.TextChannel,messages:int=50):
        text=f"LAST {messages} LINES OF {channel.name}\n\n"
        with open(f"{client.dir}/logs/{channel.id}.txt", "r") as f:
            for line in f.readlines()[-messages:]:
                text+=line
        with open(f"{client.dir}/logs/temp.txt", "w", encoding="utf-8") as f:
            print(text, file=f)
        await client.modLog.send(file=discord.File(f"{client.dir}/logs/temp.txt"))

        await ctx.send(f"{ctx.author.mention}, the requested channel(s)'s recent messages have been sent to {client.modLog.mention}!")

    @slash.slash(
        name="warn",
        description="If the warnings are a multiple of three, it will suggest a mute. 9 warnings suggests a ban.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="member",
                description="The member to warn.",
                option_type=6, # user
                required=True
            ),
            create_option(
                name="message",
                description="Optionally send a message alongside the warning.",
                option_type=3, #str
                required=False
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _warn(ctx:SlashContext,member:discord.Member,message:str=None):
        _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time
        client.Data[member.id]["warnCount"]+=1
        warnCt=client.Data[member.id]["warnCount"]

        if not warnCt%3 and warnCt:
            if warnCt<9: recc="muting"
            else: recc="banning"

            await client.modLog.send(f"{client.modRole.mention}s, {member.display_name}'s warn count is `{warnCt}`! I'd recommend {recc} them.")

        if message:
            try:
                await member.send(f"Dear, {member.display_name},\n\n{message}\n\n\t\tSincerely, The Basement Staff Team")
                await client.modLog.send(f"```{_dt} {ctx.author.mention} sent {member.mention}\n\"{message}\"")
            except discord.errors.Forbidden:
                await ctx.send(f"Couldn't directly message {member.display_name}. Maybe they have \"accept direct messages\" off...")
                return

        await ctx.send("Success!")

    @slash.slash(
        name="clear",
        description="Removes messages in the current channel. Defaults to 20.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="amount",
                description="The number of messages to delete.",
                option_type=4, #int
                required=False
            ),
            create_option(
                name="contains",
                description="A word or phrase that the deleted messages should contain.",
                option_type=3, #str
                required=False
            ),
            create_option(
                name="user",
                description="The author of the deleted messages.",
                option_type=6, #user
                required=False
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _clear(ctx:SlashContext,amount:int=20,contains:str=None,user:discord.Member=None):

        _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time

        def isUser(m:discord.Message):
            return m.author.id==user.id
        def isContained(m:discord.Message):
            return contains in m.content.lower()
        def isUC(m:discord.Message):
            return isUser(m) and isContained(m)

        if user and not contains: del_:list[discord.Message]=await ctx.channel.purge(limit=amount, check=isUser)

        elif contains and not user: del_:list[discord.Message]=await ctx.channel.purge(limit=amount, check=isContained)

        elif contains and user: del_:list[discord.Message]=await ctx.channel.purge(limit=amount, check=isUC)

        elif not (user or contains): del_:list[discord.Message]=await ctx.channel.purge(limit=amount)

        else: return await ctx.send("There was a serious error during execution of this command. Please contact Josh Smith.")

        with open(f"{client.dir}/logs/{ctx.channel_id}.txt","a") as f:
            print(f"{_dt} - {ctx.author.display_name} ({ctx.author.name}) bulk deleted {amount} messages with contains=\"{contains}\", user=\"{ctx.author.name}#{ctx.author.discriminator}\" params",file=f)

        await client.modLog.send(f"```{_dt} {ctx.author.name} deleted {amount} messages from #{ctx.channel.name}```")
        await ctx.send(f"Successfully deleted {amount} messages.")

    @slash.slash(
        name="msgs",
        description="Get you or your friends basement message count!",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="user",
                description="Specify someone other than you.",
                option_type=6, #user
                required=False
            )
        ]
    )
    async def _msgcount(ctx:SlashContext,user=None):
        if not user: user=ctx.author
        msgC=client.Data[user.id]["msgCount"]
        await ctx.send(f"{user.display_name}'s message count: {msgC}")

    @slash.slash(
        name="log",
        description="Sends a list of online members to #mog-logging.",
        guild_ids=GUILDS,
        default_permission=False
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _log(ctx:SlashContext):
        online,o,dt_str="",0,datet.now().strftime("%m/%d/%Y %H:%M:%S")
        for kiddie in client.basement.members:
            if kiddie.raw_status!="offline" and kiddie.bot==False:
                online+=" - "+kiddie.display_name+"\n"
                o+=1

        await client.modLog.send(f"{o} online members at `{dt_str}`:```\n{online}```") # send to #modlogging
        await ctx.send(f"Success!")

    @slash.slash(
        name="retrieve",
        description="Uploads an entire log or member data file. Use /recent instead for recent messages.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="channel",
                description="Retrieves an channel's entire log file.",
                option_type=7, #channels
                required=False
            ),
            create_option(
                name="member",
                description="Retrieves a member's data.",
                option_type=6, #user
                required=False
            ),
            create_option(
                name="other",
                description="Retrieve entire JSON file or last 192 lines of the Master Log.",
                option_type=3,
                required=False,
                choices=[
                    create_choice(
                        value="master",
                        name="Master Log"
                    ),
                    create_choice(
                        value="json",
                        name="JSON"
                    )
                ]
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _retrieve(ctx:SlashContext,channel:discord.TextChannel=None,member:discord.Member=None,other:str=None):

        if channel:
            await client.modLog.send(file=discord.File(f"{client.dir}/logs/{channel.id}.txt"))

        elif member:
            await client.modLog.send(f"```json\n{client.Data[member.id]}\n```")

        elif other:
            if other=="master":
                with open(f"{client.dir}/logs/{other}.txt",'r') as f:
                    latest="LAST 192 LINES FROM MASTER LOG"+"".join(f.readlines()[-192:])
                with open(f"{client.dir}/logs/temp.txt",'w') as f:
                    print(latest,file=f)
                await client.modLog.send(file=discord.File(f"{client.dir}/logs/temp.txt"))
            elif other=="json":
                await client.modLog.send(file=discord.File(f"{client.dir}/bb.{other}"))
            else:
                await ctx.send(f"There was a fatal error during code execution. Please contact Josh Smith.")
                return

        else:
            await ctx.send(f"There was a fatal error during code execution. Please contact Josh Smith.")
            return

        await ctx.send(f"The requested files were uploaded to {client.modLog.mention}.")

    @slash.slash(
        name="create",
        description="Creates a new data entry for the specified member.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="member",
                description="The member whose data entry will be created.",
                option_type=6, #user
                required=True
            ),
            create_option(
                name="join_time",
                description="The time and date that the member joined. Must be MM/DD/YYYY HH:MM:SS",
                option_type=3, #str
                required=False
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _create(ctx:SlashContext,member:discord.Member,join_time:str=None):
        if not join_time: join_time=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time
        create(client.Data, member.id, member.name, join_time)
        await ctx.send(f"Sucessfully created memeber {member.display_name}, {member.mention}!")
        await client.modLog.send(f"{member.name}'s new data:```py\n\"{member.id}\": {client.Data[member.id]}\n```")

    @slash.slash(
        name="announce",
        description="Send an announcemnt that pings everybody in #announcements.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="message",
                description="This will go after \"@Children,\" so no need to begin with a mention.",
                option_type=str,
                required=True
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _announce(ctx:SlashContext,message:str):
        await client.announcementC.send(f"{client.kRole.mention}, {message}") # sends the announcement to the #announcements channel.... mention kiddie role
        await ctx.send(f"Success!")

    @slash.slash(
        name="statistics",
        description="The #counting statistics for you or another member.",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="member",
                description="Gets another person's statistics.",
                option_type=6,
                required=False
            )
        ]
    )
    async def _stats(ctx:SlashContext,member:discord.Member=None):
        if not member: member=ctx.author

        fails:int=client.Data[member.id]["countFails"]
        high:int=client.Data[member.id]["countHigh"]
        totalHigh:int=client.Data["high"]

        percent=(high/totalHigh)*100

        stats=f"Count Fails: `{fails}`\nHighest number: `{high}`, which is `{round(percent,2)}%` of the highscore!"

        await ctx.send(f"Here are the {client.counting.mention} statistics for {member.display_name}:\n{stats}")

    @slash.slash(
        name="reconnect",
        description="Fully shuts down the bot and loads it back up.",
        guild_ids=GUILDS,
        default_permission=False
    )
    # only @staff and @basementIT can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            ),
            create_permission(
                id=888234155391975435,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _reconnect(ctx:SlashContext):
        _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S")
        save(client.Data)
        await ctx.send("Reconnecting...")
        await client.modLog.send(f"```{_dt} {ctx.author.name} disconnected bot.```")
        await client.close()
        del client.Data
        print("Reconnecting...")
        #profanity_filter.restore_profane_word_dictionaries()
        system("python3.9 bb.py")

    @slash.slash(
        name="snowflake",
        description="Returns the creation date of the Discord ID given.",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="object_id",
                description="Any Discord ID",
                option_type=str,
                required=True
            )
        ]
    )
    async def _snowflake(ctx:SlashContext,object_id:str):
        createTime=discord.Object(int(object_id)).created_at.astimezone(client.localTZ).strftime("%m/%d/%Y %H:%M:%S")
        await ctx.send(f"Object with ID of `{object_id}` was created at `{createTime} CST`")

    @slash.slash(
        name="setraw",
        description="Edits BasementBot's raw data stored for the specified member.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="member",
                description="Any Basement member.",
                option_type=6, #user
                required=True
            ),
            create_option(
                name="data_type",
                description="A BasementBot data type. There are many. This took forever to program.",
                option_type=3, #str
                required=True,
                choices=[
                    create_choice(name="Warn Count",value="warnCount"),
                    create_choice(name="Mute Count",value="muteCount" ),
                    create_choice(name="Ban Count",value="banCount"),
                    create_choice(name="Birthday",value="birthday"),
                    create_choice(name="Message Count",value="msgCount"),
                    create_choice(name="Highest Counting Score",value="msgCount"),
                    create_choice(name="Old Permission Level",value="permLvl"),
                    create_choice( name="Counting Fails",value="countFails"),
                    create_choice(name="Join Date",value="joinDate"),
                    create_choice(name="Old Mute Check",value="isMuted")
                ]
            ),
            create_option(
                name="new_value",
                description="The new value for data_type. Do not ***** this up or Josh will be mad.",
                option_type=3,
                required=True
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _setraw(ctx:SlashContext,member:discord.Member,data_type:str,new_value:str):

        newValueType=type(client.Data[member.id][data_type])

        if newValueType==bool:
            newValueType=new_value.lower()=="true"

        client.Data[member.id][data_type]=newValueType(new_value)

        await ctx.send("Success!")

    @slash.slash(
        name="deprecated",
        description="Lists how many commands have been deprecated.",
        guild_ids=GUILDS
    )
    async def _deprecated(ctx:SlashContext):
        deplist=", ".join(DEPRECATED)
        await ctx.send(f"Josh Smith has converted the following commands to slash commands ({len(DEPRECATED)} total): `{deplist}`")

    @slash.slash(
        name="help",
        description="Will return the message description associated with each command.",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="command",
                description="Optionally query a specific command.",
                option_type=3, #str
                required=False
            )
        ]
    )
    async def _help(ctx:SlashContext, command:str=None):
        "Will return the message description associated with each command."
        embed=discord.Embed(
            title="Help command",
            description="Each command and it's usage.",
            color=discord.Color.blue()
        )
        if command and command[0]!="/": command="/"+command
        if not command or command in ["\n"+cmd for cmd in dir(slashCmds) if not cmd.startswith("__")]:
            help=parseDesciptions(command)
            #map(embed.add_field,help,help.values())
            for cmd in help: embed.add_field(name=f"/{cmd}",value=help[cmd],inline=False)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(
                title="Error",
                description=f"I couldnt find the command: `{command}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @slash.slash(
        name="blacklist",
        description="All blacklisted word operations stem from this command.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="add",
                description="Will add the word you enter into the blacklisted words list.",
                option_type=3, #str
                required=False
            ),
            create_option(
                name="remove",
                description="If the word exists in the list, it will be removed.",
                option_type=3, #str
                required=False
            ),
            create_option(
                name="list",
                description="Will print out a list of the blacklisted words in #mod-logging.",
                option_type=5, #bool
                required=False
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _blw(ctx:SlashContext,add:str=None,remove:str=None,list:str=None):
        "All blacklisted word operations stem from this command."
        if add:
            word=add.lower()
            if word not in client.Data["blw"]:
                client.Data["blw"]+=[word]
                #profanity_filter.extra_profane_word_dictionaries["en"].add(word)
                await ctx.send("Successfully added a new word to the blacklist.")
            else:
                await ctx.send("That word already exists in the list!")
        elif remove:
            word=remove.lower()
            if word in client.Data["blw"]:
                client.Data["blw"].remove(word)
                #profanity_filter.extra_profane_word_dictionaries["en"].remove(word)
                await ctx.send("Successfully deleted that word from the blacklist.")
            else:
                await ctx.send("That word isn't in the blacklist!")
        elif list:
            listed=", ".join(f"||{i}||" for i in client.Data["blw"])
            await client.modLog.send(f"{ctx.author.mention} here is a list of very naughty words:\n{listed}")
            await ctx.send(f"Success!")
        else:
            await ctx.send(f"Seriously? You gotta add an option, bud...")

    @slash.slash(
        name="hash",
        description="Returns the SHA-256 hash of the input text.",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="text",
                description="Encoded into utf-8 bytes.",
                option_type=3, #str
                required=True
            )
        ]
    )
    async def _sha(ctx:SlashContext, text:str):
        hashed=sha(text.encode()).hexdigest()
        embed=discord.Embed(color=discord.Color.blue())
        embed.add_field(name="SHA256 SUM",value=f"```fix\n{hashed}```")
        await ctx.send(embed=embed)

    @slash.slash(
        name="birthdays",
        description="Will list all of the birthdays!",
        guild_ids=GUILDS
    )
    async def _birthdays(ctx:SlashContext):
        embed=discord.Embed(color=discord.Color.blue())
        embeds=[embed]
        #bdaylist="\n".join(f"<@{member}>: {client.Data[member]['birthday']}" for member in client.Data if type(member)==int and client.Data[member]['birthday'])
        bdaylist,multiple="",False
        for member in client.Data:
            if type(member)==int and client.Data[member]['birthday']:
                if len(bdaylist)<1000:
                    bdaylist+=f"<@{member}>: {client.Data[member]['birthday']}\n"
                else:
                    embeds[-1].add_field(name="Some of the birthdays!",value=bdaylist[:-1])
                    multiple=True
                    embeds+=[discord.Embed(color=discord.Color.blue())]
                    bdaylist=""
                    bdaylist+=f"<@{member}>: {client.Data[member]['birthday']}\n"
        
        if not bdaylist: bdaylist="None!"
        embeds[-1].add_field(name=f"{'More birthdays!' if multiple else 'All the birthdays!'}",value=bdaylist)
        await ctx.send(embeds=embeds)

    @slash.slash(
        name="setbday",
        description="Adds or modifies your birthday entry in BasementBot's list.",
        guild_ids=GUILDS,
        options=[
            create_option(
                name="month",
                description="Month",
                option_type=4, #int
                required=True,
                choices=[
                    create_choice(name="January",value=1),
                    create_choice(name="February",value=2),
                    create_choice(name="March",value=3),
                    create_choice(name="April",value=4),
                    create_choice(name="May",value=5),
                    create_choice(name="June",value=6),
                    create_choice(name="July",value=7),
                    create_choice(name="August",value=8),
                    create_choice(name="September",value=9),
                    create_choice(name="October",value=10),
                    create_choice(name="November",value=11),
                    create_choice(name="December",value=12)
                ]
            ),
            create_option(
                name="day",
                description="Day",
                option_type=4, #int
                required=True,
                #choices=[create_choice(name=str(i),value=i) for i in range(1,32)]
            )
        ]
    )
    async def _setbday(ctx:SlashContext,month:int,day:int):
        if not 1<=day<=31:
            #error
            embed=discord.Embed(
                title="Error!",
                description="Specify a valid date!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            day=str(day)
            month=str(month)
            if len(day)<2: day="0"+day
            if len(month)<2: month="0"+month

            if client.Data[ctx.author_id]['birthday']: old=' from `'+client.Data[ctx.author_id]['birthday']+'`'
            else: old=''
            client.Data[ctx.author_id]['birthday']=f"{month}/{day}"
            embed=discord.Embed(
                title="Success!",
                description=f"Your birthday was changed to `{client.Data[ctx.author_id]['birthday']}`{old}.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @slash.slash(
        name="modinfo",
        description="Will retrieve the member's mute count, warn count, ect.",
        guild_ids=GUILDS,
        default_permission=False,
        options=[
            create_option(
                name="member",
                description="Can be anyone except for bots.",
                option_type=6, #member
                required=True
            )
        ]
    )
    # only @staff can use this command
    @slash.permission(
        guild_id=GUILDS[0],
        permissions=[
            create_permission(
                id=STAFF_ID,
                id_type=1,
                permission=True
            )
        ]
    )
    async def _modinfo(ctx:SlashContext,member:discord.Member):
        if member.bot: await ctx.send("Why? Why would you ignore the command description...? No bots!!!")
        else:
            embed=discord.Embed(title=member.display_name,color=discord.Color.blue())
            for attr in client.Data[member.id]:
                if attr not in ["countHigh","countFails","isMuted","birthday"]:
                    embed.add_field(name=convertAttr(attr),value=f"```{client.Data[member.id][attr]}```")#,inline=False)
            await ctx.send(embed=embed)

####################################################################################################

@slash.slash(
    name="test",
    description="Runs a diagnostic on the bot and prints results to console.",
    guild_ids=GUILDS,
    default_permission=False
)
# only @staff and @basementIT can use this command
@slash.permission(
    guild_id=GUILDS[0],
    permissions=[
        create_permission(
            id=STAFF_ID,
            id_type=1,
            permission=True
        ),
        create_permission(
            id=888234155391975435,
            id_type=1,
            permission=True
        )
    ]
)
async def _test(ctx:SlashContext):
    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S") # current time

    print(f"{_dt} responed to {ctx.author.name} via /test command.")
    daignostHeader="="*8+" DIAGNOSTICS REPORT "+"="*8
    report="\n"+daignostHeader+f"""\nMain data size: {getsizeof(client.Data)}b\tSlash Size: {getsizeof(slash)}b"""
    print(report)
    fname="_warn"
    print(getattr(slashCmds,fname).__doc__)
    await ctx.send(f"Sucessfully tested, {ctx.author.mention}!")

@slash.slash(
    name="testembed",
    description="Testing command for Disocrd embeds.",
    guild_ids=GUILDS,
    default_permission=False
)
@slash.permission(
    guild_id=GUILDS[0],
    permissions=[
        create_permission(
            id=STAFF_ID,
            id_type=1,
            permission=True
        ),
        create_permission(
            id=888234155391975435,
            id_type=1,
            permission=True
        )
    ]
)
async def _embtest(ctx:SlashContext):
    "Testing command for Disocrd embeds."
    embed=discord.Embed(
        title="Test title",
        description="a description",
        color=discord.Color.blue()
    )
    embed.set_author(name="This is the author")
    embed.add_field(
        name="test field 1",
        value="```test field value 1```",
        inline=True
    )
    embed.add_field(
        name="test field 2",
        value="```test field value 2```",
        inline=True
    )
    embed.add_field(name="\u200b",value="\u200b",inline=False)
    embed.add_field(
        name="test field 3",
        value="```test field value 3```",
        inline=True
    )
    embed.add_field(
        name="test field 4",
        value="```test field value 4```",
        inline=True
    )
    #embed.set_image(url="https://cdn.discordapp.com/icons/858065227722522644/e708a44944ffd06fd9745d495f9c16c9.webp")
    await ctx.send(embed=embed)

print(f"Loaded entire code in {dt()-st}s!")
client.run(token)
