# Discord Avatar Tracker

A Python-based bot that tracks and saves Discord user profile pictures (PFPs) to Google Drive. The bot periodically checks for updates to user profile pictures and uploads them to Google Drive if they are different from the last saved version.

---

## Features

- **Profile Picture Tracking**: Fetches and downloads Discord user profile pictures.
- **Google Drive Integration**: Saves profile pictures to a specified Google Drive folder.
- **Image Comparison**: Compares the latest profile picture with the last saved version on Google Drive to avoid duplicate uploads.
- **Automatic Cleanup**: Deletes temporary files after processing to keep the workspace clean.
- **Periodic Updates**: Automatically checks for updates at a configurable interval.

---

## Prerequisites

1. **Python 3.8+**: Ensure Python is installed on your system.
2. **Discord Bot**: Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
3. **Google Cloud Service Account**:
   - Set up a service account on [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the Google Drive API.
   - Download the service account credentials JSON file.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/discord-avatar-tracker.git
   cd discord-avatar-tracker
   ```
