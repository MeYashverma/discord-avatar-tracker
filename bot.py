import discord
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import requests
import io
import os
import asyncio
from dotenv import load_dotenv

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

        # Authenticate with Google Drive using service account credentials
        print("Authenticating with Google Drive...")
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        print("Google Drive authentication successful.")

        service = build('drive', 'v3', credentials=creds)
        print("Google Drive service built successfully.")

        # Upload file to a shared folder (optional)
        shared_folder_id = '1V_hnXF2eufyok92DlaDAD4_GRkp-oRxc'  # Replace with your shared folder ID
        file_metadata = {
            'name': f'{user.name}_{user.discriminator}_profile.png',
            'parents': [shared_folder_id]  # Add this line if using a shared folder
        }
        media = io.BytesIO(response.content)
        media.seek(0)  # Ensure the file pointer is at the start

        # Use MediaIoBaseUpload for in-memory file uploads
        media_body = MediaIoBaseUpload(media, mimetype='image/png')

        print("Uploading file to Google Drive...")
        file = service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id'
        ).execute()
        print(f"Profile picture of {user.name}#{user.discriminator} saved to Google Drive with ID: {file.get('id')}")
    except HttpError as error:
        print(f"An error occurred during the upload: {error}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading profile picture: {e}")

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

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await process_users()

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)