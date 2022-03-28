# BasementBot

Created by Josh Smith 07/12/2021.

Uses Discord API and slash commands.
Uses JSON to store client data when offline.

## Requirements

### Files
Add `./logs/` directory. 
Add `./env` file containing `bottoken=<BOT'S TOKEN>`.

### Python - pip
Run `python3.9 -m pip install discord.py discord-py-slash-command pytz dotenv` to install python packages.

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
