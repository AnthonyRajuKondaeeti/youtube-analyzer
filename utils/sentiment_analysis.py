"""
YouTube Comment Sentiment Analysis Module

This Python module provides functionality for performing sentiment analysis on YouTube comments using a pre-trained transformer model. It processes cleaned comment text to classify sentiments as positive, neutral, or negative, and computes confidence scores for each classification.

Features:
- Sentiment classification of YouTube comments using a RoBERTa-based model
- Support for batch processing with progress tracking
- Output includes sentiment labels and confidence scores
- Integration with pandas DataFrames for seamless data handling
- Robust handling of text truncation for long comments

Architecture:
- Utilizes Hugging Face's transformers library for model and tokenizer
- Leverages PyTorch for model inference
- Integrates with pandas for DataFrame manipulation
- Uses tqdm for progress visualization during processing

Dependencies:
- pandas: DataFrame handling and manipulation
- numpy: Numerical operations for softmax calculation
- transformers: Hugging Face library for tokenizer and model
- torch: PyTorch for model inference
- tqdm: Progress bar for processing feedback

Author: Anonymous
Version: 1.0
"""

import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

# Initialize tokenizer and model for sentiment analysis
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
labels = ["Negative", "Neutral", "Positive"]

def get_sentiment(text):
    """
    Classify the sentiment of a single comment.
    
    Processes a comment text using a pre-trained RoBERTa model to determine its sentiment
    (Negative, Neutral, Positive) and compute a confidence score.
    
    Args:
        text (str): The cleaned comment text to analyze
        
    Returns:
        tuple: (sentiment, confidence) where sentiment is the predicted label and
               confidence is the probability score for the predicted class
    """
    encoded_input = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        output = model(**encoded_input)
    scores = output.logits[0].numpy()
    probs = np.exp(scores) / np.sum(np.exp(scores))  # softmax
    sentiment = labels[np.argmax(probs)]
    confidence = float(np.max(probs))
    return sentiment, confidence

def analyze_comments(comments_df):
    """
    Perform sentiment analysis on a DataFrame of comments.
    
    Applies sentiment analysis to the 'cleaned_comment' column of the input DataFrame,
    adding 'sentiment' and 'confidence' columns with results.
    
    Args:
        comments_df (pd.DataFrame): DataFrame containing a 'cleaned_comment' column
        
    Returns:
        pd.DataFrame: Input DataFrame with added 'sentiment' and 'confidence' columns
    """
    tqdm.pandas()
    comments_df[["sentiment", "confidence"]] = comments_df["cleaned_comment"].progress_apply(
        lambda x: pd.Series(get_sentiment(x))
    )
    return comments_df