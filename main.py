import requests
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from drive_auth import get_drive
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
USER_ID = os.getenv('USER_ID')

if not DISCORD_TOKEN or not USER_ID:
    raise ValueError("DISCORD_TOKEN and USER_ID must be set in the environment variables.")

def get_user_avatar():
    try:
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
        url = f"https://discord.com/api/v10/users/{USER_ID}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        avatar_hash = data.get('avatar')
        username = data.get('username', 'unknown')
        discriminator = data.get('discriminator', '0000')

        if not avatar_hash:
            print("No avatar found for the user.")
            return

        avatar_url = f"https://cdn.discordapp.com/avatar/{USER_ID}/{avatar_hash}.png?size=1024"
        filename = f"{username}_{discriminator}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        print(f"Downloading avatar from {avatar_url}")
        image = requests.get(avatar_url).content
        with open(filename, 'wb') as f:
            f.write(image)

        print(f"Uploading {filename} to Google Drive...")
        drive = get_drive()
        file = drive.CreateFile({'title': filename})
        file.SetContentFile(filename)
        file.Upload()

        print("Upload complete. Cleaning up...")
        os.remove(filename)
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(get_user_avatar, 'interval', hours=12)

try:
    print("Starting scheduler...")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Shutting down scheduler...")
    scheduler.shutdown()
