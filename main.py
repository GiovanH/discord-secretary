import discord
import discord.ext.commands
import logging
import re
import traceback
import subprocess
import os
import shutil

from pathlib import Path

import config

TEXT_ROOT = "./textfiles/"

intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(
    command_prefix='/',
    intents=intents
)

def writeTxt(new_content, dest, warn):
    destpath = Path(TEXT_ROOT) / dest
    # try:
    with open(destpath, 'a') as fp:
        fp.write(new_content + '\n')
    # except OSError:
    #     if warn:
    #         warn(f"WARN:\n```text\n{traceback.format_exc()}```")
    #     # Pcloud over rclone does not like seek/append sometimes
    #     prev_content = ""
    #     if os.path.isfile(destpath):
    #         with open(destpath, 'r') as fp:
    #             prev_content = fp.read()
    #         shutil.move(destpath, str(destpath) + '.bak')

    #     with open(destpath, 'w') as fp:
    #         fp.write(prev_content + new_content + '\n')

@bot.listen()
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    topic = message.channel.topic
    content = message.content
    warn = message.channel.send

    deleted = False

    async def processCommand(cmdstr, content):
        nonlocal deleted
        print(f"{cmdstr=} {content=}")
        args = cmdstr.split(' ')
        if args[0] == "WRITE":
            dest = args[1]
            writeTxt(content, dest, warn=warn)
            return

        elif args[0] == "WRITENL":
            # raise NotImplementedError()
            dest = args[1]
            writeTxt('', dest, warn=warn)
            return

        elif args[0] == "ECHO":
            await message.channel.send(content)
            return

        elif args[0] == "DELETE" and not deleted:
            deleted = True
            await message.delete()
            return

        else:
            raise NotImplementedError(cmdstr)

    if not topic:
        return

    # Run commands and iterate
    try:
        # message.add_reaction('💭')
        for cmdstr in re.split(r'[;]|\n', topic):
            await processCommand(cmdstr, content)

        if not deleted:
            await message.add_reaction('✔')

    # Failed to process
    except:
        await message.channel.send(f"```text\n{traceback.format_exc()}```")
        try:
            if not deleted:
                await message.add_reaction('✖')
        except:
            pass

if __name__ == "__main__":
    bot.run(config.token)
