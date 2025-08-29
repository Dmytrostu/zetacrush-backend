#!/usr/bin/env python
"""
Google Drive Setup Helper Script

This script helps you test your Google Drive API credentials and folder access.
"""
import os
import sys
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def check_environment():
    """Check if required environment variables are set."""
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    issues = []
    
    if not folder_id:
        issues.append("GOOGLE_DRIVE_FOLDER_ID is not set in your .env file")
    
    if not os.path.exists(creds_file):
        issues.append(f"Credentials file '{creds_file}' not found")
    
    return issues

def test_upload(test_file=None):
    """Test uploading a file to Google Drive."""
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    # If no test file is provided, create a simple text file
    if not test_file:
        test_file = "test_upload.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for Google Drive upload.")
    
    try:
        # Set up credentials
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=SCOPES)
        
        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # File metadata
        file_metadata = {
            'name': os.path.basename(test_file),
            'parents': [folder_id]
        }
        
        # Upload file
        media = MediaFileUpload(
            test_file,
            resumable=True
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink', '')
        
        print(f"✅ Success! File uploaded to Google Drive.")
        print(f"File ID: {file_id}")
        print(f"Web link: {web_link}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error uploading to Google Drive: {str(e)}")
        return False

def main():
    """Main function to check Google Drive setup."""
    print("🔍 Checking Google Drive setup...")
    
    # Check environment
    issues = check_environment()
    if issues:
        print("❌ Found setup issues:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues and try again. See docs/google_drive_setup.md for help.")
        sys.exit(1)
    
    # Check credentials file
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    try:
        with open(creds_file, "r") as f:
            creds_data = json.load(f)
            print(f"✅ Credentials file loaded successfully")
            print(f"  Service account email: {creds_data.get('client_email')}")
            
            # Remind user to share folder with service account
            print(f"\n⚠️ Important: Make sure your Google Drive folder is shared with this email address!")
    except Exception as e:
        print(f"❌ Error reading credentials file: {str(e)}")
        sys.exit(1)
    
    # Test upload
    print("\n🔄 Testing file upload to Google Drive...")
    if test_upload():
        print("\n✅ Your Google Drive setup is working correctly!")
    else:
        print("\n❌ Google Drive setup test failed. Check the error message above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
