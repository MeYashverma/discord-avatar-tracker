import discord
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import io
import os
import schedule
import time

# --- Discord Bot Setup ---
DISCORD_BOT_TOKEN = 'MTM2Nzc1Njc0Mzg4Njc3MDE5Ng.GiG53h.588oa2v4gJ6z98Sc87emsB-OUZmLFiunR2BZ2w'
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# --- Google Drive Setup ---
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- List of User IDs to process ---
USER_IDS_TO_SAVE = [1296939414655729674]

async def save_profile_to_drive(user: discord.User):
    if not user:
        print(f"User not found.")
        return

    avatar_url = user.avatar.url if user.avatar else user.default_avatar_url
    try:
        response = requests.get(avatar_url)
        response.raise_for_status()

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file']
        )

        try:
            service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': f'{user.name}_{user.discriminator}_profile.png'}
            media = io.BytesIO(response.content)
            file = service.files().create(body=file_metadata, media_body=media, mimeType='image/png').execute()
            print(f"Profile picture of {user.name}#{user.discriminator} saved to Google Drive with ID: {file.get('id')}")
        except HttpError as error:
            print(f'An error occurred: {error}')

    except requests.exceptions.RequestException as e:
        print(f"Error downloading profile picture: {e}")

async def process_users():
    for user_id in USER_IDS_TO_SAVE:
        user = client.get_user(user_id)
        if user:
            await save_profile_to_drive(user)
        else:
            print(f"User with ID {user_id} not found.")

def schedule_task():
    schedule.every().hour.do(lambda: client.loop.create_task(process_users()))

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    schedule_task()
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Keep the bot running and check for scheduled tasks

if __name__ == "__main__":
    import asyncio
    client.run(DISCORD_BOT_TOKEN)