import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# === CONFIGURATION ===
# Path to your service account .json file
SERVICE_ACCOUNT_FILE = 'service-account.json' 
# The ID of the Google Drive folder to read from
DRIVE_FOLDER_ID = '1XV7c_GausSwTsqumpvBo7SET4f6Gq-eg'
# The ID of the Google Sheet to write to (replace with your spreadsheet ID)
SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'
# Range in the Google Sheet (e.g., 'Sheet1!A1')
SHEET_RANGE = 'Sheet1!A2'

# Scopes required for Drive and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

def authenticate():
    """Authenticates using the service account and returns Drive and Sheets services."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    return drive_service, sheets_service

def list_files_in_folder(drive_service, folder_id):
    """Lists files in a specific Google Drive folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        fields="nextPageToken, files(id, name, mimeType, createdTime)"
    ).execute()
    return results.get('files', [])

def get_file_content(drive_service, file_id, mime_type):
    """Reads the content of a file. Supports text/plain and Google Docs."""
    try:
        if mime_type == 'application/vnd.google-apps.document':
            # Export Google Doc as plain text
            return drive_service.files().export(fileId=file_id, mimeType='text/plain').execute().decode('utf-8')
        elif mime_type == 'text/plain':
            return drive_service.files().get_media(fileId=file_id).execute().decode('utf-8')
        else:
            return f"[Unsupported File Type: {mime_type}]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

def summarize_text(text):
    """Placeholder for summarization logic.
    You could use an AI API here (like Gemini or OpenAI) or simple logic.
    """
    if not text or text.startswith('['):
        return "No content to summarize"
    
    # Simple logic: first 100 characters as a placeholder
    summary = text[:100].replace('\n', ' ') + "..."
    return summary

def update_spreadsheet(sheets_service, spreadsheet_id, data):
    """Appends data rows to the Google Sheet."""
    body = {
        'values': data
    }
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=SHEET_RANGE,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f"Updated {result.get('updates').get('updatedCells')} cells.")

def main():
    try:
        drive_service, sheets_service = authenticate()
        
        print(f"Reading files from folder: {DRIVE_FOLDER_ID}...")
        files = list_files_in_folder(drive_service, DRIVE_FOLDER_ID)
        
        if not files:
            print("No files found.")
            return

        rows_to_add = []
        for file in files:
            print(f"Processing: {file['name']}...")
            
            # Step 1: Read content
            content = get_file_content(drive_service, file['id'], file['mimeType'])
            
            # Step 2: Summarize
            summary = summarize_text(content)
            
            # Step 3: Prepare row data [Filename, Created Time, Summary]
            rows_to_add.append([
                file['name'],
                file['createdTime'],
                summary
            ])

        # Step 4: Write to Sheets
        if rows_to_add:
            print(f"Syncing to Google Sheet: {SPREADSHEET_ID}...")
            update_spreadsheet(sheets_service, SPREADSHEET_ID, rows_to_add)

    except HttpError as error:
        print(f"An error occurred: {error}")
    except FileNotFoundError:
        print(f"Error: {SERVICE_ACCOUNT_FILE} not found. Please place your service account JSON in the project folder.")

if __name__ == '__main__':
    main()
