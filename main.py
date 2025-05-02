import discord
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from PIL import Image, ImageChops
import requests
import io
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import glob

# Load environment variables
load_dotenv()

# --- Discord Bot Setup ---
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Use environment variable for security
print(f"DISCORD_BOT_TOKEN: {DISCORD_BOT_TOKEN}")
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# --- Google Drive Setup ---
SERVICE_ACCOUNT_FILE = 'discord-avatar-tracker-458606-c982a6d97395.json'

# --- List of User IDs to process ---
USER_IDS_TO_SAVE = [1296939414655729674]

# --- Timer Configuration ---
SAVE_INTERVAL = 1  # Time interval in minutes for the next save

async def save_profile_to_drive(user: discord.User):
    if not user:
        print(f"User not found.")
        return

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    try:
        print(f"Downloading avatar from: {avatar_url}")
        response = requests.get(avatar_url)
        response.raise_for_status()
        print("Avatar downloaded successfully.")

        # Save the new image to a temporary file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_image_path = f"{user.id}_{timestamp}.png"
        with open(new_image_path, "wb") as f:
            f.write(response.content)

        # Authenticate with Google Drive using service account credentials
        print("Authenticating with Google Drive...")
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        print("Google Drive authentication successful.")

        service = build('drive', 'v3', credentials=creds)
        print("Google Drive service built successfully.")

        # Find the last saved image on Google Drive
        print("Fetching the last saved image from Google Drive...")
        query = f"name contains '{user.id}_' and mimeType='image/png' and trashed=false"
        results = service.files().list(q=query, orderBy="createdTime desc", pageSize=1, fields="files(id, name)").execute()
        files = results.get('files', [])

        last_saved_image_path = None
        if files:
            last_saved_file = files[0]
            last_saved_file_id = last_saved_file['id']
            last_saved_file_name = last_saved_file['name']
            print(f"Last saved file found: {last_saved_file_name} (ID: {last_saved_file_id})")

            # Download the last saved image
            last_saved_image_path = f"{user.id}_last_saved.png"
            request = service.files().get_media(fileId=last_saved_file_id)
            with open(last_saved_image_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download progress: {int(status.progress() * 100)}%")
            print("Last saved image downloaded successfully.")

            # Compare the new image with the last saved image
            print("Comparing the new image with the last saved image...")
            new_image = Image.open(new_image_path)
            last_saved_image = Image.open(last_saved_image_path)

            diff = ImageChops.difference(new_image, last_saved_image)
            if not diff.getbbox():
                print("The new image is identical to the last saved image. Skipping upload.")
                # Cleanup temporary files
                os.remove(new_image_path)
                os.remove(last_saved_image_path)
                return
            else:
                print("The new image is different from the last saved image. Proceeding with upload.")
        else:
            print("No previous image found on Google Drive. Proceeding with upload.")

        # Upload the new image to Google Drive
        shared_folder_id = '1V_hnXF2eufyok92DlaDAD4_GRkp-oRxc'  # Replace with your shared folder ID
        file_metadata = {
            'name': f'{user.id}_{timestamp}.png',
            'parents': [shared_folder_id]
        }
        media = io.BytesIO(response.content)
        media.seek(0)  # Ensure the file pointer is at the start

        media_body = MediaIoBaseUpload(media, mimetype='image/png')

        print("Uploading file to Google Drive...")
        file = service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id'
        ).execute()
        print(f"Profile picture of {user.name}#{user.discriminator} saved to Google Drive with ID: {file.get('id')}")

        # Cleanup temporary files
        os.remove(new_image_path)
        if last_saved_image_path:
            os.remove(last_saved_image_path)

    except HttpError as error:
        print(f"An error occurred during the upload: {error}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading profile picture: {e}")
    finally:
        # Ensure cleanup happens even if an exception occurs
        if os.path.exists(new_image_path):
            os.remove(new_image_path)
        if last_saved_image_path and os.path.exists(last_saved_image_path):
            os.remove(last_saved_image_path)

async def process_users():
    for user_id in USER_IDS_TO_SAVE:
        try:
            print(f"Fetching user with ID: {user_id}")
            user = await client.fetch_user(user_id)
            if user:
                print(f"Processing user: {user.name}#{user.discriminator}")
                await save_profile_to_drive(user)
            else:
                print(f"User with ID {user_id} not found.")
        except Exception as e:
            print(f"An error occurred while processing user {user_id}: {e}")

async def countdown_timer():
    while True:
        for remaining in range(SAVE_INTERVAL * 60, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"Time remaining for next save: {timer}", end="\r")
            await asyncio.sleep(1)
        print("\nStarting the next save...")
        await process_users()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await countdown_timer()

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)