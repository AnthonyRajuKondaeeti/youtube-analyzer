"""
YouTube API Utility Module

This Python module provides utility functions for interacting with the YouTube Data API and YouTube Transcript API to extract video metadata, comments, and transcripts. It is designed for integration into a YouTube video analysis application, offering robust error handling and retry logic for API operations.

Features:
- Extraction of YouTube video IDs from URLs
- Retrieval of video metadata (title, channel name) using the YouTube Data API
- Fetching of video comments with pagination support
- Robust transcript extraction with language preference, fallback mechanisms, and translation
- Comprehensive logging for debugging API interactions
- Retry logic for handling transient API errors

Architecture:
- Modular design with functions for specific API tasks
- Integration with Google API client and YouTubeTranscriptApi libraries
- Use pandas for structured data output
- Regular expressions for URL parsing
- Error handling for API limitations and failures

Dependencies:
- google-api-python-client: For YouTube Data API interactions
- youtube-transcript-api: For transcript extraction
- pandas: DataFrame creation and manipulation
- re: Regular expression for URL parsing
- logging: Debugging and monitoring
- time: Retry delay management

Author: Anonymous
Version: 1.0
"""

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import pandas as pd
import logging
import time

def extract_video_id(url):
    """
    Extract YouTube video ID from a URL.
    
    Parses a YouTube URL to retrieve the 11-character video ID using regular expressions.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str or None: 11-character video ID if found, None otherwise
    """
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_youtube_service(api_key):
    """
    Initialize YouTube Data API service.
    
    Creates a service object for interacting with the YouTube Data API v3.
    
    Args:
        api_key (str): YouTube Data API key
        
    Returns:
        googleapiclient.discovery.Resource: YouTube API service object
    """
    return build("youtube", "v3", developerKey=api_key)

def get_video_details(youtube, video_id):
    """
    Retrieve video metadata from YouTube Data API.
    
    Fetches the title and channel name for a given video ID.
    
    Args:
        youtube (googleapiclient.discovery.Resource): YouTube API service object
        video_id (str): YouTube video ID
        
    Returns:
        tuple or None: (video_title, channel_name) if successful, None on failure
    """
    try:
        # Create the request to get the video details
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        
        # Execute the request
        response = request.execute()
        
        # Check if the response contains the expected data
        if 'items' in response and len(response['items']) > 0:
            video_title = response['items'][0]['snippet']['title']
            channel_name = response['items'][0]['snippet']['channelTitle']
            return video_title, channel_name
        else:
            logging.error(f"Video details not found for video ID: {video_id}")
            return None  # Return None if no items are found in the response
    
    except Exception as e:
        # Catch any exceptions and log them
        logging.error(f"Error fetching video details for video ID {video_id}: {e}")
        return None  # Return None in case of any error

def get_comments(youtube, video_id, max_comments=100):
    """
    Fetch comments for a YouTube video.
    
    Retrieves up to the specified number of top-level comments with pagination.
    
    Args:
        youtube (googleapiclient.discovery.Resource): YouTube API service object
        video_id (str): YouTube video ID
        max_comments (int, optional): Maximum number of comments to fetch (defaults to 100)
        
    Returns:
        pandas.DataFrame: DataFrame containing comment data (comment, author, published_at, like_count)
    """
    comments = []
    next_page_token = None
    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        )
        response = request.execute()
        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment": top_comment["textDisplay"],
                "author": top_comment["authorDisplayName"],
                "published_at": top_comment["publishedAt"],
                "like_count": top_comment["likeCount"]
            })
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return pd.DataFrame(comments)

def get_transcript(video_id, language_code='en', max_retries=3):
    """
    Fetch video transcript with robust error handling and fallback mechanisms.
    
    Attempts to retrieve a transcript in the specified language, with retries and
    fallback to generated or alternative language transcripts if needed.
    
    Args:
        video_id (str): YouTube video ID
        language_code (str, optional): Preferred language code (defaults to 'en')
        max_retries (int, optional): Maximum retry attempts (defaults to 3)
    
    Returns:
        pandas.DataFrame: Transcript DataFrame with columns ['text', 'start', 'duration'],
                         or empty DataFrame if all attempts fail
    """
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempting to fetch transcript (attempt {attempt + 1}/{max_retries})")
            
            # Try to fetch in the requested language (English by default)
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
            
            # Validate that we got actual data
            if not transcript_data:
                logging.warning(f"Empty transcript data received for video {video_id}")
                continue
                
            # Create DataFrame and validate
            df = pd.DataFrame(transcript_data)
            if df.empty:
                logging.warning(f"Empty DataFrame created from transcript data")
                continue
                
            logging.info(f"Successfully fetched transcript with {len(df)} segments")
            return df
            
        except NoTranscriptFound:
            logging.warning(f"No transcript found for language {language_code}, trying fallback methods...")
            break  # Don't retry for NoTranscriptFound, go to fallback
            
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                logging.error(f"All {max_retries} attempts failed, trying fallback methods...")
                break
    
    # Fallback methods if direct fetch failed
    try:
        logging.info("Trying fallback transcript methods...")
        transcript_obj = YouTubeTranscriptApi.list_transcripts(video_id)
        fallback = None

        # Try exact match first
        for t in transcript_obj:
            if t.language_code == language_code:
                fallback = t
                break

        # Try generated transcripts if no exact match
        if not fallback:
            generated = [t for t in transcript_obj if t.is_generated]
            fallback = generated[0] if generated else None

        # Try any available transcript if still no match
        if not fallback:
            available = list(transcript_obj)
            fallback = available[0] if available else None

        if fallback:
            logging.info(f"Using fallback transcript in: {fallback.language_code}")

            # Translate if not English and translatable
            if fallback.language_code != language_code and fallback.is_translatable:
                logging.info(f"Translating from {fallback.language_code} to {language_code}")
                try:
                    fallback = fallback.translate(language_code)
                except Exception as translate_error:
                    logging.warning(f"Translation failed: {translate_error}, using original language")

            # Fetch with retry logic
            for attempt in range(max_retries):
                try:
                    transcript_data = fallback.fetch()
                    
                    # Validate data
                    if not transcript_data:
                        logging.warning(f"Empty fallback transcript data")
                        continue
                        
                    df = pd.DataFrame(transcript_data)
                    if df.empty:
                        logging.warning(f"Empty DataFrame from fallback transcript")
                        continue
                        
                    logging.info(f"Successfully fetched fallback transcript with {len(df)} segments")
                    return df
                    
                except Exception as fetch_error:
                    logging.error(f"Fallback attempt {attempt + 1} failed: {fetch_error}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    continue
        else:
            logging.warning("No transcript available in any language or format")

    except (TranscriptsDisabled, Exception) as e:
        logging.error(f"Transcript fallback error: {e}")

    # Return empty DataFrame with expected columns if all methods fail
    logging.warning("All transcript fetch methods failed, returning empty DataFrame")
    return pd.DataFrame(columns=['text', 'start', 'duration'])