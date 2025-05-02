import requests
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockScheduler

DISCORD_TOKEN = ''
USER_ID = ''

def get_user_avatar():
    headers = {
        "Authorization":f"Bot {DISCORD_TOKEN}"
    }
    url = f"https://discord.com/api/v10/users/{USER_ID}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        avatar_hash = data['avatar']
        username = data['username']
        discriminator = data['discriminator']

        avatar_url = f"https://cdn.discordapp.com/avatar/{USER_ID}/{avatar_hash}.png?size=1024"
        filename = f"{username}_{discriminator}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        print(f"Downloading avatar from {avatar_url}")
        image = requests.get(avatar_url).content
        with open(filename, 'wb') as f:
            f.write(image)

        print(f"Uploading {filename} to Google Drive...")
        drive = get_drive()
        file = drive.CreateFile({'title':filename})
        file.SetContentFile(filename)
        file.upload()

        print("Upload complete. Cleaning up...")
        os.remove(filename)
    else:
        print("Failed to upload the file")

scheduler = BlockScheduler()
scheduler.add_job(get_user_avatar,'interval',hours=12)
schedular.start()
