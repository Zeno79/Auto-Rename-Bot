from pyrogram import Client, filters
import re
from datetime import datetime

renaming_operations = {}

# Patterns for extracting episode numbers and quality
pattern_episode = re.compile(r'S(\d+)(?:E|EP)(\d+)')
pattern_quality = re.compile(r'\d{3,4}p')

def extract_episode_number(filename):
    match = re.search(pattern_episode, filename)
    if match:
        return match.group(2)  # Extracted episode number
    return None

def extract_quality(filename):
    match = re.search(pattern_quality, filename)
    if match:
        return match.group(0)  # Extracted quality
    return "Unknown"

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_files(client, message):
    user_id = message.from_user.id
    file_name = message.document.file_name if message.document else (message.video.file_name if message.video else message.audio.file_name)

    # Extract episode number and quality
    episode_number = extract_episode_number(file_name)
    quality = extract_quality(file_name)

    # Create a new name and a sharing link for the file
    format_template = "[S01E{episode}] Wind Breaker [Dual] {quality}p @YourBot.mkv"
    new_file_name = format_template.format(episode=episode_number or "Unknown", quality=quality)

    # Generate a fake URL based on message ID (simulating t.me link)
    file_url = f"https://t.me/File_Store/{message.message_id}"

    # Formatting the final output as per your example
    response_text = f"{file_url} -n 4{new_file_name}"

    # Send the renamed file as a formatted link
    await message.reply_text(response_text)

    # Optionally, mark the operation as done (for renaming tracking)
    renaming_operations[message.message_id] = datetime.now()

# Example of calling the bot
client = Client("my_bot")
client.run()
