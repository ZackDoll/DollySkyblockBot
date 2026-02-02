import datetime
from openai import OpenAI

from scrapingant_client import ScrapingAntClient

from typing import Final
import os

import requests
from bs4 import BeautifulSoup
import time
import asyncio

from dotenv import load_dotenv

from discord import Intents, Client, Message

# loads token so user cant see
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)
URL = "https://hypixel.net/forums/skyblock-patch-notes.158/"
BASE = "https://hypixel.net"
SAVE_FILE = "last_seen.txt"
SUBSCRIBERS_FILE = "subscribers.txt"
subscriber_ids = []

global last_seen_link
global last_seen_sticky_link

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        last_seen_link = f.read().strip()
else:
    last_seen_link = None

# just in case pinned patch is new
STICKY_SAVE_FILE = "last_seen_sticky.txt"
if os.path.exists(STICKY_SAVE_FILE):
    with open(STICKY_SAVE_FILE, "r") as f:
        last_seen_sticky_link = f.read().strip()
else:
    last_seen_sticky_link = None

if os.path.exists(SUBSCRIBERS_FILE):
    with open(SUBSCRIBERS_FILE, "r") as f:
        subscriber_ids = [int(line.strip()) for line in f if line.strip()]
else:
    print(f"Warning: {SUBSCRIBERS_FILE} not found. Creating new file.")
    # creates the file only if it doesn't exist
    open(SUBSCRIBERS_FILE, "w").close()

chatgptClient = OpenAI(
    api_key=os.getenv("CHATGPT_API_KEY")
)
# old system
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
# patch_notes_text = post_body.get_text(separator="\n")
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

    user_message = message.content.strip()

    # command to subscribe
    if user_message.lower() == "!subscribe":
        user_id = message.author.id

        # check if already subscribed
        if user_id in subscriber_ids:
            await message.channel.send(f"{message.author.mention} you're already subscribed!")
            return
        # add to subscribers file
        with open(SUBSCRIBERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

        # also add to runtime list
        subscriber_ids.append(user_id)

        await message.channel.send(f"{message.author.mention} subscribed to patch notes!")

    elif user_message.lower() == "!unsubscribe":
        user_id = message.author.id

        if user_id not in subscriber_ids:
            await message.channel.send(f"{message.author.mention} you're not subscribed!")
            return
        # remove from runtime list
        subscriber_ids.remove(user_id)
        # rewrite file without this user
        with open(SUBSCRIBERS_FILE, "w") as f:
            for sub_id in subscriber_ids:
                f.write(f"{sub_id}\n")

        await message.channel.send(f"{message.author.mention} unsubscribed from patch notes!")


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
        response = chatgptClient.responses.create(
            model="gpt-4-turbo",
            instructions="You are a summarizer",
            input=
            f"summarize the Hypixel SkyBlock patch notes below. follow these rules EXACTLY:\n\n"
            f"1. include EVERY SINGLE change mentioned, no exceptions\n"
            f"2. for numerical changes, format as: [item]: [old value] → [new value]\n"
            f"3. for non-numerical changes, list exactly what changed\n"
            f"4. group into categories: new features, balance changes, bug fixes, other changes\n"
            f"5. use bullet points and sub-bullets to match the original structure\n"
            f"6. if a bullet point has sub-items, include ALL sub-items\n"
            f"7. ignore only bug reporting instructions or feedback request sections\n\n"
            f"CRITICAL RULES:\n"
            f"- if something was added, removed, changed, buffed, nerfed, or standardized → include it\n"
            f"- if a rarity changed → include it\n"
            f"- if a multiplier was removed → include it\n"
            f"- missing even ONE change is unacceptable\n\n"
            f"DO NOT add any commentary, postamble, or explanation about how you followed the rules.\n"
            f"DO NOT say things like 'this summary adheres to' or 'all changes listed'.\n"
            f"output ONLY the summary itself, nothing else.\n\n"
            f"PATCH NOTES:\n{patch_notes_text}"
        )
        text = response.output_text
        # sends message to all subscribers
        for sub_id in subscriber_ids:
            user = await client.fetch_user(sub_id)
            await user.send("a new patch has been received!")
            await send_long_message(user, text)
            await user.send(f"link to post: {link_to_post}")

    except Exception as e:
        print(f"Error: {e}")


async def scan_for_updates():
    global last_seen_link
    global last_seen_sticky_link
    while True:
        print(f"Scanned at {datetime.datetime.now()}")
        try:
            response = scraper.general_request(URL, browser=False)
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print("link Unavailable")
            print(f"error log: {e}")
            await asyncio.sleep(600)
            continue

        # get all thread containers
        all_threads = soup.select("div.structItem")

        # track if we found threads
        found_sticky = False
        found_normal = False

        # loop through threads to check sticky and normal
        for thread in all_threads:
            thread_element = thread.select_one("div.structItem-title a")

            if not thread_element:
                continue

            new_link = BASE + thread_element["href"]
            thread_title = thread_element.get_text(strip=True)

            # check parent for sticky class
            parent = thread.parent
            parent_classes = parent.get("class", []) if parent else []
            is_sticky = "structItemContainer-group--sticky" in parent_classes

            # check sticky thread (any sticky thread)
            if is_sticky and not found_sticky:
                found_sticky = True
                print(f"sticky thread: {thread_title}")

                if new_link != last_seen_sticky_link:
                    print(f"new sticky thread detected: {thread_title}")
                    print(f"link: {new_link}")
                    last_seen_sticky_link = new_link
                    with open(STICKY_SAVE_FILE, "w") as f:
                        f.write(last_seen_sticky_link)

                    try:
                        post_response = scraper.general_request(new_link, browser=False)
                        soup_post = BeautifulSoup(post_response.content, "html.parser")
                        post_body = soup_post.find("div", class_="bbWrapper")

                        if post_body:
                            patch_notes_text = post_body.get_text(separator="\n")
                            await send_update_message(patch_notes_text, new_link)
                        else:
                            print("ERROR: could not find post body in sticky thread!")
                    except Exception as e:
                        print(f"error processing sticky thread: {e}")

            # check normal thread (first non-sticky thread)
            elif not is_sticky and not found_normal:
                found_normal = True
                print(f"normal thread: {thread_title}")
                print(f"current link: {last_seen_link}")
                print(f"top link: {new_link}")
        #what
                if new_link != last_seen_link:
                    print(f"new thread detected: {thread_title}")
                    print(f"link: {new_link}")
                    last_seen_link = new_link
                    # changes saved link to new_link
                    with open(SAVE_FILE, "w") as f:
                        f.write(last_seen_link)

                    try:
                        post_response = scraper.general_request(new_link, browser=False)
                        soup_post = BeautifulSoup(post_response.content, "html.parser")
                        post_body = soup_post.find("div", class_="bbWrapper")

                        if post_body:
                            patch_notes_text = post_body.get_text(separator="\n")
                            await send_update_message(patch_notes_text, new_link)
                        else:
                            print("ERROR: could not find post body!")
                    except Exception as e:
                        print(f"error processing normal thread: {e}")

            # stop once we've checked both types
            if found_sticky and found_normal:
                break

        if not found_normal:
            print("normal thread not found")

        print(f"stored links - normal: {last_seen_link}, sticky: {last_seen_sticky_link}")
        await asyncio.sleep(600)


@client.event
async def on_ready() -> None:
    global scraper
    print(f"{client.user} is now running")
    print("initializing scraper")
    scraper = ScrapingAntClient(token=os.getenv('SCRAPINGANT_API_KEY'))
    print("scraper is set up")
    client.loop.create_task(scan_for_updates())


def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()