from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import os
import re

# File renaming operations are tracked here
renaming_operations = {}

# Extract patterns to find episode numbers and quality
pattern_episode = re.compile(r'S(\d+)[^\d]*(\d+)')  # S01E01 type format
pattern_quality = re.compile(r'(\d{3,4}p)', re.IGNORECASE)  # e.g., 1080p

def extract_episode_number(filename):
    match = re.search(pattern_episode, filename)
    if match:
        return match.group(2)  # Return episode number if matched
    return None

def extract_quality(filename):
    match = re.search(pattern_quality, filename)
    if match:
        return match.group(1)  # Return quality (e.g., 1080p)
    return "Unknown"

@Client.on_message(filters.private & filters.document)
async def auto_rename_files(client, message):
    user_id = message.from_user.id
    file_id = message.document.file_id
    file_name = message.document.file_name

    # Avoid multiple rename operations on the same file
    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            return  # Ignore if the file was recently renamed

    # Mark the file for renaming
    renaming_operations[file_id] = datetime.now()

    # Extract episode number and quality
    episode_number = extract_episode_number(file_name)
    quality = extract_quality(file_name)

    # Define your renaming format template
    format_template = "ShowName_S01_E{episode}_{quality}"  # Modify as needed

    # Replace placeholders with actual values
    if episode_number:
        format_template = format_template.replace("{episode}", episode_number)
    else:
        format_template = format_template.replace("{episode}", "Unknown")

    format_template = format_template.replace("{quality}", quality)

    # Create new file name with the extension
    _, file_extension = os.path.splitext(file_name)
    new_file_name = f"{format_template}{file_extension}"

    # Download the file locally with the new name
    file_path = f"downloads/{new_file_name}"
    download_msg = await message.reply_text("Downloading file...")
    try:
        path = await client.download_media(message=document, file_name=file_path)
    except Exception as e:
        del renaming_operations[file_id]  # Clear renaming flag
        return await download_msg.edit(f"Download failed: {e}")

    # Upload the renamed file to Telegram
    upload_msg = await download_msg.edit("Uploading file...")
    try:
        sent_message = await client.send_document(
            chat_id=message.chat.id,
            document=path,
            caption=f"**{new_file_name}**"
        )
    except Exception as e:
        os.remove(file_path)
        del renaming_operations[file_id]
        return await upload_msg.edit(f"Upload failed: {e}")

    # Generate Telegram file sharing link
    file_url = f"https://t.me/{sent_message.chat.username}/{sent_message.message_id}"

    # Clean up local file and complete the process
    os.remove(file_path)
    del renaming_operations[file_id]

    await upload_msg.edit(f"File uploaded successfully: [Download Link]({file_url})")
    
