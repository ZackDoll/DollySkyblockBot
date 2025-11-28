import datetime
from openai import OpenAI

import cloudscraper

from typing import Final
import os

import requests
from bs4 import BeautifulSoup
import time
import asyncio

from dotenv import load_dotenv

from discord import Intents, Client, Message

#loads token so user cant see
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

scraper = cloudscraper.create_scraper()

intents: Intents = Intents.default()
intents.message_content = True #NOQA
client: Client = Client(intents = intents)
URL = "https://hypixel.net/forums/skyblock-patch-notes.158/"
BASE = "https://hypixel.net"
SAVE_FILE = "last_seen.txt"

global last_seen_link
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        last_seen_link = f.read().strip()
else:
    last_seen_link = None

chatgptClient = OpenAI(
    api_key = os.getenv("CHATGPT_API_KEY")
)
#old system
'''
async def send_message(message:Message, user_message: str, uName: str) -> None:
    try:
        if not user_message:
            print("intents not enabled")
        else:
            return



        if str(message.channel) == "sb-updates":
            link_start = user_message.index('h')
            link_end = user_message.rfind('/')
            if link_end == -1 or link_start == -1:
                return
            else:
                url = user_message[link_start:link_end]
                headers = {"User-Agent": "Mozilla/5.0"}

                textBlob = requests.get(url, headers=headers)
                soup = BeautifulSoup(textBlob.text, "html.parser")

                post_body = soup.find("div", class_="bbWrapper"'''
#patch_notes_text = post_body.get_text(separator="\n")
'''
                response = chatgptClient.responses.create(
                    model="gpt-4-turbo",
                    instructions="You are a summarizer",
                    input=f"{patch_notes_text} Summarize this and make note of every single change and bullet point them",
                )
                user_id = 281265330846695425
                user = await client.fetch_user(user_id)
                await user.send("A new patch has been received!")
                await user.send(response.output_text)
                
        else:
            return

    except Exception as e:
        print(e)
        '''

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username = (message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}]  {username}: {user_message}")
    # doesn't exist in this version
    #await send_message(message, user_message, username)

async def send_long_message(user, text, limit=1800):
    # Split text into lines
    lines = text.split("\n")
    current_chunk = ""

    for line in lines:
        # Check if adding this line exceeds the limit
        if len(current_chunk) + len(line) + 1 > limit:
            # Send the current chunk
            await user.send(current_chunk)
            current_chunk = ""  # Reset chunk

        # Add the line to the current chunk
        if current_chunk:
            current_chunk += "\n" + line
        else:
            current_chunk = line

    # Send any remaining text
    if current_chunk:
        await user.send(current_chunk)


async def send_update_message(patch_notes_text, link_to_post):
    try:
        user_id = 281265330846695425
        user_id2 = 491078725073633291

        user = await client.fetch_user(user_id)
        user2 = await client.fetch_user(user_id2)
        response = chatgptClient.responses.create(
            model="gpt-4-turbo",
            instructions="You are a summarizer",
            input=
                f"You are a strict summarizer. "
                f"If you exceed this limit, your answer is invalid. "
                f"Summarize the patch notes below, noting every single change, "
                f"bullet point them, and group into categories. "
                f"List every numerical change that happens to anything specifically"
                f"Ignore any issue reporting sections. "
                f"Do not include extra commentary. "
                f"Be concise but complete. "
                f"PATCH NOTES: {patch_notes_text}"
        )
        await user.send("A new patch has been received!")
        await user2.send("A new patch has been received!")
        text = response.output_text
        await send_long_message(user, text)
        await send_long_message(user2, text)

        await user.send(f"Link to post: {link_to_post}")
        await user2.send(f"Link to post: {link_to_post}")
    except Exception as e:
        print(f"Error: {e}")

async def scan_for_updates():
    global last_seen_link
    while True:
        print(f"Scanned at {datetime.datetime.now()}")
        response = scraper.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")

        thread_element = soup.select_one("div.structItem-title a")

        if thread_element:
            new_link = BASE + thread_element["href"]
            thread_title = thread_element.get_text(strip=True)
            print(f"Current Link: {last_seen_link}")
            print(f"Top Link: {new_link}")

            if new_link and new_link != last_seen_link:
                print(f"New thread detected: {thread_title}")
                print(f"Link: {new_link}")
                last_seen_link = new_link
                #changes saved link to new_link
                with open(SAVE_FILE, "w") as f:
                    f.write(last_seen_link)

                # checks the link for stuff
                post_response = scraper.get(new_link)
                soup = BeautifulSoup(post_response.text, "html.parser")

                post_body = soup.find("div", class_="bbWrapper")
                patch_notes_text = post_body.get_text(separator="\n")

                await send_update_message(patch_notes_text, last_seen_link)
        else:
            print("Thread Element not found")
        print(last_seen_link)
        await asyncio.sleep(300)

@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running")
    client.loop.create_task(scan_for_updates())

def main() -> None:
    client.run(token = TOKEN)

if __name__ == "__main__":
    main()





