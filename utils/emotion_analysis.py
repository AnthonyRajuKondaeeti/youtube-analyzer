"""
YouTube Transcript Emotion Analysis Module

This Python module provides functionality for performing emotion analysis on YouTube video transcripts using a pre-trained transformer model. It classifies the emotional content of transcript segments and assigns confidence scores, enabling insights into the emotional tone of the video.

Features:
- Emotion classification of transcript text using a DistilRoBERTa-based model
- Processes transcript segments with progress tracking
- Outputs emotion labels (e.g., joy, anger, sadness) and confidence scores
- Integrates with pandas DataFrames for seamless data handling
- Handles text truncation for long inputs to fit model constraints

Architecture:
- Utilizes Hugging Face's transformers library for model inference
- Employs a pipeline for simplified emotion classification
- Leverages pandas for DataFrame manipulation
- Uses tqdm for progress visualization during processing

Dependencies:
- transformers: Hugging Face library for pipeline and model
- pandas: DataFrame handling and manipulation
- tqdm: Progress bar for processing feedback

"""

from transformers import pipeline
import pandas as pd
from tqdm import tqdm

# Initialize emotion classification pipeline with DistilRoBERTa model
emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

def extract_emotion(x):
    """
    Classify the emotion of a single transcript segment.
    
    Processes a text segment using a pre-trained DistilRoBERTa model to determine its
    dominant emotion (e.g., joy, anger, sadness) and confidence score.
    
    Args:
        x (str): The transcript text segment to analyze (truncated to 512 characters)
        
    Returns:
        pd.Series: Series containing the emotion label and confidence score,
                   or ["Unknown", 0] if analysis fails
    """
    result = emotion_pipeline(x[:512])
    if result:
        top_emotion = result[0][0]
        return pd.Series([top_emotion["label"], top_emotion["score"]])
    else:
        return pd.Series(["Unknown", 0])

def analyze_transcript(transcript_df):
    """
    Perform emotion analysis on a transcript DataFrame.
    
    Applies emotion classification to the 'text' column of the input DataFrame,
    adding 'emotion' and 'emotion_score' columns with results.
    
    Args:
        transcript_df (pd.DataFrame): DataFrame containing a 'text' column with transcript segments
        
    Returns:
        pd.DataFrame: Input DataFrame with added 'emotion' and 'emotion_score' columns
    """
    tqdm.pandas()
    transcript_df[["emotion", "emotion_score"]] = transcript_df["text"].progress_apply(extract_emotion)
    return transcript_df
