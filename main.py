"""
YouTube Video Transcript and Comment Analysis Script

This Python script serves as the core processing logic for a YouTube video analysis application. It extracts video transcripts and comments, performs sentiment and emotion analysis, extracts keywords, and generates visualizations to provide insights into video content and audience reactions.

Features:
- Extraction of YouTube video transcripts and comments using the YouTube API
- Support for multi-language transcript extraction
- Sentiment analysis of comments and emotion analysis of transcripts
- Keyword extraction from transcripts using YAKE
- Generation of visualizations (stacked area charts, heatmaps, and sentiment distributions)
- Robust file management and cleanup for output data
- Comprehensive logging for debugging and monitoring

Architecture:
- Modular design with utility functions for API interactions, preprocessing, and analysis
- File-based output for CSV, text, and image files
- Error handling and logging for robust operation
- Integration with Flask for web-based applications

Dependencies:
- pandas: Data manipulation and CSV handling
- dotenv: Environment variable management for API key
- Custom modules: youtube_api, preprocess, sentiment_analysis, emotion_analysis, keyword_transcript, visualization
- logging: System logging for debugging
- os: File system operations

"""

import os
from dotenv import load_dotenv
from utils import youtube_api, preprocess, sentiment_analysis, emotion_analysis, keyword_transcript, visualization
import logging
import pandas as pd

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables and API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

def seconds_to_mmss(seconds):
    """
    Convert seconds to MM:SS format for timestamps.
    
    Handles conversion of time values for display in transcript data, ensuring
    consistent formatting.
    
    Args:
        seconds (float or None): Time in seconds to convert
        
    Returns:
        str: Formatted time string in MM:SS format, or "00:00" if input is invalid
    """
    if pd.isna(seconds):
        return "00:00"
    total_seconds = int(float(seconds))
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def format_transcript_timestamps(transcript_df, video_id=None):
    """
    Format transcript timestamps and add clickable YouTube links.
    
    Processes a transcript DataFrame to convert 'start' times to MM:SS format
    and optionally adds hyperlinks to the YouTube video at specific timestamps.
    
    Args:
        transcript_df (pd.DataFrame): DataFrame containing transcript data
        video_id (str, optional): YouTube video ID for generating timestamp links
        
    Returns:
        pd.DataFrame: Modified DataFrame with formatted timestamps and reordered columns
    """
    if transcript_df is None or transcript_df.empty:
        return transcript_df
    df_copy = transcript_df.copy()
    if 'start' not in df_copy.columns:
        logging.warning("'start' column not found in transcript dataframe")
        return df_copy
    df_copy['start_seconds'] = df_copy['start'].copy()
    if video_id:
        df_copy['timestamp'] = df_copy['start'].apply(
            lambda x: f'<a href="https://www.youtube.com/watch?v={video_id}&t={int(float(x))}s" target="_blank">{seconds_to_mmss(x)}</a>' if pd.notna(x) else "00:00"
        )
    else:
        df_copy['timestamp'] = df_copy['start'].apply(seconds_to_mmss)
    columns = df_copy.columns.tolist()
    if 'start' in columns:
        columns.remove('start')
    if 'timestamp' in columns:
        columns.remove('timestamp')
        columns.insert(0, 'timestamp')
    if 'start_seconds' in columns:
        columns.remove('start_seconds')
        columns.append('start_seconds')
    df_copy = df_copy[columns]
    return df_copy

def cleanup_existing_files(out_dir):
    """
    Remove existing output files to prevent stale data.
    
    Cleans up specified files in the output directory to ensure fresh data for
    each analysis run.
    
    Args:
        out_dir (str): Directory containing output files
    """
    files_to_cleanup = [
        "full_text.txt",
        "transcript_emotion_keywords.csv",
        "top_keywords_yake.csv",
        "comments_with_sentiment.csv",
        "emotion_stacked_area.png",
        "emotion_heatmap.png"
    ]
    for filename in files_to_cleanup:
        filepath = os.path.join(out_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logging.info(f"Removed existing file: {filepath}")
            except OSError as e:
                logging.warning(f"Could not remove {filepath}: {e}")

def main(video_url, language='en', out_dir="static/data"):
    """
    Main function for video transcript and comment analysis.
    
    Orchestrates the extraction, processing, and analysis of YouTube video
    transcripts and comments, saving results to the output directory.
    
    Args:
        video_url (str): YouTube video URL to analyze
        language (str, optional): Language code for transcript (defaults to 'en')
        out_dir (str, optional): Directory for saving output files (defaults to 'static/data')
        
    Returns:
        tuple: (comments_df, transcript_df, video_title, channel_name) or (None, None, None, None) on error
    """
    try:
        logging.info("Extracting video ID from URL")
        video_id = youtube_api.extract_video_id(video_url)
        if not video_id:
            logging.error("Could not extract video ID from URL")
            return None, None, None, None

        logging.info(f"Extracted video ID: {video_id}")
        youtube = youtube_api.get_youtube_service(API_KEY)
        video_details = youtube_api.get_video_details(youtube, video_id)

        if video_details is None:
            logging.error(f"Failed to retrieve video details for video ID {video_id}")
            return None, None, None, None

        video_title, channel_name = video_details
        logging.info(f"Video title: {video_title}, Channel name: {channel_name}")

        os.makedirs(out_dir, exist_ok=True)
        cleanup_existing_files(out_dir)

        logging.info("Fetching comments")
        try:
            comments_df = youtube_api.get_comments(youtube, video_id, max_comments=300)
            logging.info(f"Successfully fetched {len(comments_df)} comments")
        except Exception as e:
            logging.error(f"Failed to fetch comments: {e}")
            comments_df = pd.DataFrame(columns=['comment', 'author', 'published_at', 'like_count'])

            # Cleanup old comments file
            comments_file = os.path.join(out_dir, "comments_with_sentiment.csv")
            if os.path.exists(comments_file):
                try:
                    os.remove(comments_file)
                    logging.info(f"Removed stale comments file: {comments_file}")
                except Exception as e:
                    logging.warning(f"Could not remove comments file: {e}")

        logging.info("Fetching transcript")
        transcript_df = None
        try:
            transcript_df = youtube_api.get_transcript(video_id, language)
            if transcript_df is None or transcript_df.empty:
                logging.warning("Transcript not found or unavailable.")
                transcript_df = None
            else:
                required_columns = ['text', 'start', 'duration']
                missing_columns = [col for col in required_columns if col not in transcript_df.columns]
                if missing_columns:
                    logging.error(f"Transcript missing required columns: {missing_columns}")
                    transcript_df = None
                else:
                    logging.info("Analyzing emotions in transcript")
                    transcript_df = emotion_analysis.analyze_transcript(transcript_df)
                    logging.info("Converting timestamps to MM:SS format and adding video URLs")
                    transcript_df = format_transcript_timestamps(transcript_df, video_id)

        except Exception as e:
            logging.error(f"Unexpected error during transcript fetching: {e}")
            transcript_df = None

        if transcript_df is None or transcript_df.empty:
            logging.info("Transcript missing — cleaning up transcript text and graphs.")
            for file in ["full_text.txt", "transcript_emotion_keywords.csv", "emotion_stacked_area.png", "emotion_heatmap.png"]:
                filepath = os.path.join(out_dir, file)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        logging.info(f"Removed file: {filepath}")
                    except Exception as e:
                        logging.warning(f"Could not remove {filepath}: {e}")

        if not comments_df.empty:
            logging.info("Cleaning comments")
            comments_df["cleaned_comment"] = comments_df["comment"].apply(preprocess.clean_text)
            logging.info("Analyzing sentiment")
            try:
                comments_df = sentiment_analysis.analyze_comments(comments_df)
                comments_df.to_csv(f"{out_dir}/comments_with_sentiment.csv", index=False)
                logging.info("Saved comments with sentiment to CSV")

                # # Generate sentiment visualization
                # generate_sentiment_visualizations(comments_df, out_dir)
            except Exception as e:
                logging.error(f"Error in sentiment analysis: {e}")

        if transcript_df is not None and not transcript_df.empty:
            try:
                logging.info("Saving transcript emotion data to CSV")
                transcript_df.to_csv(f"{out_dir}/transcript_emotion_keywords.csv", index=False)

                logging.info("Extracting keywords from transcript using YAKE")
                texts = transcript_df.get("text", []).tolist()
                if texts:
                    keyword_df = keyword_transcript.extract_keywords_yake(
                        texts, top_n=15, ngram=1, output_dir=out_dir, visualize=False
                    )
                    logging.info(f"Top YAKE keywords saved to {out_dir}/top_keywords_yake.csv")
                else:
                    logging.warning("No text data found in transcript for keyword extraction")
            except Exception as e:
                logging.error(f"Error processing transcript data: {e}")

        logging.info("Data processing completed successfully.")
        return comments_df, transcript_df, video_title, channel_name

    except Exception as e:
        logging.error(f"Unexpected error in main function: {e}")
        return None, None, None, None

def generate_all_visualizations(df, output_dir="static/data"):
    """
    Generate visualizations for transcript analysis.
    
    Creates stacked area charts and heatmaps for emotion analysis and saves
    them to the output directory.
    
    Args:
        df (pd.DataFrame): DataFrame with transcript and emotion data
        output_dir (str, optional): Directory for saving visualizations (defaults to 'static/data')
    """
    if df is None or df.empty:
        logging.warning("No data provided for visualization generation")
        return
    try:
        os.makedirs(output_dir, exist_ok=True)
        start_column = 'start_seconds' if 'start_seconds' in df.columns else ('start' if 'start' in df.columns else None)
        if not start_column:
            logging.error("No time column found for visualization. Need 'start' or 'start_seconds'.")
            return

        vis_df = df.copy()
        if start_column != 'start':
            vis_df['start'] = vis_df[start_column]

        try:
            logging.info("Generating stacked area chart of emotions")
            visualization.plot_emotion_stacked_area(vis_df, output_dir)
        except Exception as e:
            logging.error(f"Error generating stacked area chart: {e}")

        try:
            logging.info("Generating heatmap of emotions")
            visualization.plot_emotion_heatmap(vis_df, output_dir)
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")

        logging.info(f"Visualization generation completed. Files saved in `{output_dir}`")

    except Exception as e:
        logging.error(f"Error in visualization generation: {e}")

def generate_sentiment_visualizations(comments_df, output_dir="static/data"):
    """
    Generate visualizations for comment sentiment analysis.
    
    Creates a sentiment distribution chart for comments and saves it to the output directory.
    
    Args:
        comments_df (pd.DataFrame): DataFrame with comment and sentiment data
        output_dir (str, optional): Directory for saving visualizations (defaults to 'static/data')
    """
    if comments_df is None or comments_df.empty:
        logging.warning("No comment data provided for sentiment visualization")
        return
    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info("Generating sentiment distribution chart")
        visualization.plot_sentiment_distribution(comments_df, output_dir)
        logging.info("Sentiment visualization saved.")
    except Exception as e:
        logging.error(f"Error generating sentiment visualization: {e}")

# if __name__ == "__main__":
#     """
#     Entry point for standalone script execution.
#     
#     Prompts for a YouTube video URL, processes it, and generates visualizations
#     if a transcript is successfully retrieved.
#     """
#     video_link = input("Paste YouTube video URL: ").strip()
#     comments_df, transcript_df, video_title, channel_name = main(video_link)
#     if transcript_df is not None:
#         generate_all_visualizations(transcript_df)
