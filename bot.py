# bot.py
import os

import discord
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate
import re
# from jisho_api.word import Word
# from jisho_api.kanji import Kanji

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TRANSLATE = os.getenv('TRANSLATE_TOKEN')

client = discord.Client()
translate_client = translate.Client.from_service_account_json(
    'googleapi.json')


@client.event
async def on_ready():
    print("もしもし")


@client.event
async def on_message(message):
    if message.author == client.user:  # base case
        return
    # so that the bot does not re-output links
    if message.content.startswith("https://"):
        return
    if message.content.startswith(":"):
        return
    # if jap is detected & the confidence is high
    if translate_client.detect_language(message.content)["language"] != "en" and translate_client.detect_language(message.content)["confidence"] > 0.05:
        transl_msg = translate_client.translate(message.content, "en", "text")[
            "translatedText"]  # transl_msg = translated form of message

        if "@" in transl_msg:
            transl_msg = transl_msg.replace("@ ", "@")

    # making the emotes format themselves properly!

        # "indices_open" is the list that contains the index's for the '<' char
        indices_open = [i.start() for i in re.finditer('<', transl_msg)]
        indices_closed = [i.start() for i in re.finditer('>', transl_msg)]
        # if there's an emote there should be equal number of < and >
        for i in range(len(indices_open)):
            # splicing each emote from transl_msg into a list of str
            emote_id = [int(s) for s in transl_msg[indices_open[i]:indices_closed[i]].split(
            ) if s.isdigit()]  # 'emote_id' is a 'list' of all the 'ids' of the emotes in 'transl_msg'
            # 'emote_object' is a object of type 'emoji' with respective 'emote_id'
            emote_object = [client.get_emoji(emote_id[i])]

            if (("<:" in transl_msg and ">" in transl_msg) or ("<a:" in transl_msg)):
                # check if the msg contains an emoji that it cannot use:
                if emote_object[i].is_usable() == False:
                    # sanitizer function
                    while True:
                        index1 = transl_msg.find('<')
                        index2 = transl_msg.find('>')
                        transl_msg = transl_msg.replace(
                            transl_msg[index1:index2], "")
                        if transl_msg.find('<') > -1:
                            break
                else:
                    transl_msg = transl_msg.replace(": ", ":")
            await message.channel.send(transl_msg)

    # for gura-chan
    if message.content == "a":
        await message.channel.send("サメです！")


client.run(TOKEN)
translate.run(TRANSLATE)
