# BasementBot v2

Created by Josh Smith 07/12/2021.

Uses Discord API and slash commands.
Uses JSON to store client data when offline.

You can find what I'm working on or planning to work [at the project page](https://github.com/purplelemons-dev/basementbot/projects/1).

## Abstract/Origin

The BasementBot was designed to "absorb" other bots on The Basement Discord server. Many lines of the code are hard-coded with IDs of various objects in The Basement Discord server, and will *not* work in any other server. I created BasementBot back in August of 2021 and have since then learned a lot about effective Python scripting, but some of the early BasementBot code is extremely convoluted and condensed because my favorite thing to do is see how many lines I can combine into one--regardless of efficiency.

I would not reccomend trying to pull code from anywhere in this repo unless you have a few things under your belt: 1) *a ton* of experience with Python, and 2) *a ton* of experience with Discord bots. Another great thing to have is being able to problem solve. A lot of the code I wrote can and will break, so problem solving will help out a ton if you want to copy my code. Speaking of copying, feel free to use whatever's in this repo however you like! I'm always open to suggestions so open an issue or start a discussion!

## Requirements

### Files
Add `./logs/` directory. 
Add `./env` file containing `bottoken=<BOT'S TOKEN>`.

### Python - pip
Run `python3.9 -m pip install discord.py discord-py-slash-command pytz dotenv` to install python packages. I'm not entirely sure that covers all the libraries used by BasementBot, but I'm sure you'll get some warnings at runtime...

## General crap
*added the following code to discord.member python file at line 235:*
```py
def __dict__(self):
    return {
        'id': f'{self_user.id}',
        'type': 'member',
        'name': f'{self._user.name}',
        'discriminator': f'{self._user.discriminator}',
        'bot': f'{self._user.bot}',
        'nick': f'{self.nick}',
        'guild': f'{self.guild}'
    }
```
*added the following code to discord.channel python file for TextChannel and VoiceChannel respectively*
```py
def __dict__(self):
    attrs = [
        ('id', self.id),
        ('type', 'text channel'),
        ('name', self.name),
        ('position', self.position),
        ('nsfw', self.nsfw),
        ('news', self.is_news()),
        ('category_id', self.category_id)
    ]
    return dict(attrs)
```
############################################
```py
def __dict__(self):
    attrs = [
        ('id', self.id),
        ('type', 'voice channel'),
        ('name', self.name),
        ('rtc_region', self.rtc_region),
        ('position', self.position),
        ('bitrate', self.bitrate),
        ('user_limit', self.user_limit),
        ('category_id', self.category_id)
    ]
    return dict(attrs)
```
*added the following code to discord.role python file for Role*
```py
def __dict__(self):
    attrs = {
        'id': self.id,
        'type': 'role',
        'name': self.name,
        'color': self._colour,
        'mentionable': self.mentionable,
        'position': self.position
    }
    return attrs
```
*added the following code to discord.emoji python file for Emoji*
```py
def __dict__(self):
    attrs={
        'id': self.id,
        'type': 'emoji',
        'name': self.name,
        'animated': self.animated,
        'managed': self.managed,
        'url': self.url.BASE+self.url._url
    }
    return attrs
```
