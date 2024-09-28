from telethon import TelegramClient
import csv
import os
from tqdm import tqdm

api_id = 'YOUR_API_ID'  # Take from here https://my.telegram.org/apps
api_hash = 'YOUR_API_HASH'  # Take from here https://my.telegram.org/apps

client = TelegramClient('session_name', api_id, api_hash)

async def export_chat():
    print("Connecting to Telegram...")
    await client.start()  # Start the client and authenticate
    print("Successfully connected!")

    # Ask the user for the chat ID or username
    chat = input("Enter the chat ID or username: ").strip()

    # Remove '@' if it's present in the username
    if chat.startswith('@'):
        chat = chat[1:]

    # Ask the user if media files should be downloaded
    download_media = input("Do you want to download media files? (y/n): ").strip().lower() == 'y'

    # Set the folder for media files
    media_folder = "downloaded_media"
    if download_media and not os.path.exists(media_folder):
        os.makedirs(media_folder)

    print(f"Exporting all messages from chat '{chat}'")

    # Attempt to retrieve the chat entity
    try:
        chat_entity = await client.get_entity(chat)
    except Exception as e:
        print(f"Error: Could not find chat '{chat}'. Please check the ID or username.")
        return

    # Count total number of messages for the progress bar
    total_messages = await client.get_messages(chat_entity, limit=0)
    total_count = total_messages.total

    # Open a file in write mode ("w") to save all messages
    with open("chat_history_with_users.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the column headers
        writer.writerow(["Date", "Full Name", "Username", "Message", "Media File"])

        # Initialize the progress bar
        message_count = 0  # Counter for processed messages

        # Initialize the progress bar and count the total number of messages
        with tqdm(desc="Exporting messages", unit="message", total=total_count, dynamic_ncols=True) as pbar:
            async for message in client.iter_messages(chat_entity, reverse=True):
                
                if message.sender_id:  # Check if the message has a sender
                    sender = await message.get_sender()  # Get information about the sender

                    if hasattr(sender, 'first_name'):  # If the sender is a user
                        full_name = sender.first_name if sender.first_name else ""
                        if sender.last_name:
                            full_name += f" {sender.last_name}"
                        username = sender.username if sender.username else "No username"
                    elif hasattr(sender, 'title'):  # If the sender is a channel or group
                        full_name = sender.title  # Use the name of the channel/group
                        username = "Channel/Group"
                    else:
                        full_name = "Unknown"
                        username = "No username"

                    # Download media file if present
                    media_path = None
                    if download_media and message.media:
                        try:
                            # Download the media file
                            media_path = await message.download_media(file=media_folder)
                        except Exception as e:
                            print(f"Error downloading media: {e}")
                    
                    # Write the date, full name, username, message text, and media path (if any) to the CSV file
                    writer.writerow([message.date, full_name, username, message.text or 'Media/Other content', media_path or ''])

                    # Increment the message count
                    message_count += 1

                    # Update the progress bar
                    pbar.update(1)

        print(f"Total messages saved: {message_count}")

with client:
    try:
        client.loop.run_until_complete(export_chat())
    except Exception as e:
        print(f"An error occurred: {e}")
