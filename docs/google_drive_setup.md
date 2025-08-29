# Google Drive Setup Guide for Zetacrush

This guide explains how to set up Google Drive for file storage in the Zetacrush backend.

## Prerequisites

1. A Google account
2. Python 3.7 or newer

## Setup Instructions

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top and select "New Project"
3. Enter a name for your project and click "Create"
4. Select your new project in the dropdown

### 2. Enable the Google Drive API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API" and select it
3. Click "Enable"

### 3. Create Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a name for your service account and click "Create"
4. Skip role assignment (or assign basic viewer role) and click "Continue"
5. Click "Done"
6. Find your new service account in the list and click on it
7. Go to the "Keys" tab and click "Add Key" > "Create new key"
8. Choose JSON format and click "Create"
9. Save the downloaded JSON file as `credentials.json` in your project directory

### 4. Create a Folder in Google Drive

1. Go to [Google Drive](https://drive.google.com/)
2. Create a new folder where you want to store uploaded files
3. Right-click on the folder and select "Get link"
4. Copy the folder ID from the URL - it's the long string after `folders/` in the URL
   Example: From `https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7`, the folder ID is `1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7`

### 5. Share the Folder with the Service Account

1. Right-click on the folder in Google Drive and select "Share"
2. In the email field, enter the service account email (found in the credentials.json file under "client_email")
3. Change the permission to "Editor"
4. Uncheck "Notify people"
5. Click "Share"

### 6. Configure Environment Variables

Add the following to your `.env` file:

```
# Google Drive Storage Settings
USE_CLOUD_STORAGE=true
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## Testing File Uploads

1. Make sure the `credentials.json` file is in your project's root directory
2. Start the FastAPI server
3. Use the upload API endpoint to upload a file
4. Check your Google Drive folder to verify the file was uploaded

## Troubleshooting

- If you get permission errors, ensure your service account has editor access to the folder
- If files aren't uploading, check that the folder ID is correct
- For any API errors, check the application logs for detailed error messages
