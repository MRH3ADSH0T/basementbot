
from dotenv import dotenv_values as dev
import discord
from discord.ext import commands
import multiprocessing as mp

client=commands.Bot(command_prefix="$")


#if __name__=="__main__":
#
#
#    client.

token=dict(dev(".env"))["examplebot"]

client.run(token)
