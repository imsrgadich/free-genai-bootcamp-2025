import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict
import re
from urllib.parse import parse_qs, urlparse
import requests
import json

# Add this at the top of the script for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["hi", "en"]):
        self.languages = languages
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not self.api_key:
            raise ValueError("YouTube API key is required")
            
        # Initialize session without OAuth headers
        self.session = requests.Session()

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if "v=" in url:
            return url.split("v=")[1][:11]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1][:11]
        return None

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL
        
        Args:
            url (str): YouTube playlist URL
            
        Returns:
            Optional[str]: Playlist ID if found, None otherwise
        """
        if "list=" in url:
            parsed_url = urlparse(url)
            return parse_qs(parsed_url.query)['list'][0]
        return None

    def get_playlist_video_ids(self, playlist_url: str) -> List[str]:
        """Get video IDs from a YouTube playlist using API key only"""
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("Invalid playlist URL")
            return []

        url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
        video_ids = []
        page_token = None

        try:
            while True:
                params = {
                    'part': 'contentDetails',
                    'playlistId': playlist_id,
                    'maxResults': 50,
                    'key': self.api_key
                }
                
                if page_token:
                    params['pageToken'] = page_token

                response = self.session.get(
                    url,
                    params=params,
                    timeout=10
                )
                
                response.raise_for_status()
                data = response.json()

                # Extract video IDs
                for item in data.get('items', []):
                    if 'contentDetails' in item and 'videoId' in item['contentDetails']:
                        video_ids.append(item['contentDetails']['videoId'])

                page_token = data.get('nextPageToken')
                if not page_token:
                    break

                time.sleep(1)  # Rate limiting

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return []

        return list(set(video_ids))

    def get_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript
        
        Args:
            video_id (str): YouTube video ID or URL
            
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Extract video ID if full URL is provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = self.extract_video_id(video_id)
            
        if not video_id:
            print("Invalid video ID or URL")
            return None

        print(f"Downloading transcript for video ID: {video_id}")
        
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """
        Save transcript to file
        
        Args:
            transcript (List[Dict]): Transcript data
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        filename = f"./transcripts/{filename}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False

    def download_playlist_transcripts(self, playlist_url: str, print_transcript: bool = False) -> Dict[str, bool]:
        """
        Download transcripts for all videos in a playlist
        
        Args:
            playlist_url (str): YouTube playlist URL
            print_transcript (bool): Whether to print transcripts
            
        Returns:
            Dict[str, bool]: Dictionary of video IDs and their download status
        """
        video_ids = self.get_playlist_video_ids(playlist_url)
        results = {}
        
        for video_id in video_ids:
            transcript = self.get_transcript(video_id)
            if transcript:
                success = self.save_transcript(transcript, video_id)
                results[video_id] = success
                if success and print_transcript:
                    print(f"\nTranscript for video {video_id}:")
                    for entry in transcript:
                        print(f"{entry['text']}")
            else:
                results[video_id] = False
                
        return results

def main(url: str, print_transcript: bool = False):
    downloader = YouTubeTranscriptDownloader()
    
    if "list=" in url:
        # Handle playlist
        results = downloader.download_playlist_transcripts(url, print_transcript)
        for video_id, success in results.items():
            status = "successfully" if success else "failed to"
            print(f"Video {video_id} {status} download transcript")
    else:
        # Handle single video
        downloader = YouTubeTranscriptDownloader()
    
        # Get transcript
        transcript = downloader.get_transcript(url)
        downloader.save_transcript(transcript, url)
        if transcript:
            # Save transcript
            video_id = downloader.extract_video_id(url)
            if downloader.save_transcript(transcript, video_id):
                print(f"Transcript saved successfully to {video_id}.txt")
                #Print transcript if True
                if print_transcript:
                    # Print transcript
                    for entry in transcript:
                        print(f"{entry['text']}")
            else:
                print("Failed to save transcript")
        
        else:
            print("Failed to get transcript")

if __name__ == "__main__":
    # Example usage for playlist
    playlist_url = "https://www.youtube.com/playlist?list=PL3SQxlU5xkuBuUMKXZYv__f4IToDZi1Dm"
    main(playlist_url, print_transcript=True)