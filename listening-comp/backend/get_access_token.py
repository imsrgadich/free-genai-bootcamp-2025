import os
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from googleapiclient.discovery import build

# Define scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_credentials():
    """Get valid user credentials from storage or create new ones."""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Access Token...")
            creds.refresh(Request())
        else:
            print("Getting new Access Token...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', 
                SCOPES,
                redirect_uri='http://localhost:8090'
            )
            # Specify port explicitly
            creds = flow.run_local_server(
                port=8090,
                prompt='consent',
                access_type='offline'
            )
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

if __name__ == '__main__':
    try:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
        credentials = get_credentials()
        print(f"\nAccess Token: {credentials.token}")
        
        # Test the credentials
        youtube = build('youtube', 'v3', credentials=credentials)
        request = youtube.channels().list(
            part="snippet",
            mine=True
        )
        response = request.execute()
        print("Authentication successful!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
