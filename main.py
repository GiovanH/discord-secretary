import discord
import discord.ext.commands
import logging
import re
import traceback

from pathlib import Path

import config

TEXT_ROOT = "./textfiles/"

intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(
    command_prefix='/',
    intents=intents
)

def writeTxt(content, dest):
    with open(Path(TEXT_ROOT) / dest, 'a') as fp:
        fp.write(content)
        fp.write('\n')

@bot.listen()
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    topic = message.channel.topic
    content = message.content

    deleted = False

    async def processCommand(cmdstr, content):
        nonlocal deleted
        print(f"{cmdstr=} {content=}")
        args = cmdstr.split(' ')
        if args[0] == "WRITE":
            dest = args[1]
            writeTxt(content, dest)
            return

        elif args[0] == "WRITENL":
            dest = args[1]
            writeTxt('', dest)
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
