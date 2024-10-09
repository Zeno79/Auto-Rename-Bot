from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
from helper.database import madflixbotz
import re

renaming_operations = {}

# Regex patterns for episode and quality extraction
pattern1 = re.compile(r'S(\d+)(?:E|EP)(\d+)')
pattern2 = re.compile(r'S(\d+)\s*(?:E|EP|-\s*EP)(\d+)')
pattern3 = re.compile(r'(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)')
patternX = re.compile(r'(\d+)')

def extract_episode_number(filename):
    match = re.search(pattern1, filename) or re.search(pattern2, filename) or re.search(pattern3, filename) or re.search(patternX, filename)
    return match.group(2) if match else None

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_files(client, message: Message):
    user_id = message.from_user.id
    file_id = message.document.file_id if message.document else message.video.file_id if message.video else message.audio.file_id
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name
    
    format_template = await madflixbotz.get_format_template(user_id)
    if not format_template:
        return await message.reply_text("Please set an auto-rename format using /autorename.")

    # Avoid duplicate renaming operations
    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            return  # Skip if file was recently renamed

    renaming_operations[file_id] = datetime.now()

    # Extract episode number from file name
    episode_number = extract_episode_number(file_name)
    if episode_number:
        format_template = format_template.replace("{episode}", str(episode_number))

    _, file_extension = os.path.splitext(file_name)
    new_file_name = f"{format_template}{file_extension}"
    
    # Create the custom file-sharing URL using the given example format
    base_url = "https://t.me/Fiile_Store/"
    file_url = f"{base_url}{file_id} -n {new_file_name}"

    # Formulate a response to include the episode number and the file-sharing URL
    response_text = f"File URL generated for Episode {episode_number}: {file_url}" if episode_number else f"File URL generated: {file_url}"

    await message.reply_text(response_text)

    # Mark the operation as complete
    del renaming_operations[file_id]
