"""
Text Preprocessing Module for YouTube Comment Analysis

This Python module provides a utility function to clean text data, specifically designed for preprocessing YouTube comments. It removes unwanted elements like URLs, converts emojis to text representations, and normalizes text for downstream sentiment analysis.

Features:
- Conversion of emojis to textual descriptions for consistent processing
- Removal of URLs to focus on comment content
- Retention of basic punctuation and alphanumeric characters
- Normalization of whitespace for clean text output
- Robust handling of non-string inputs

Architecture:
- Single-function module for text cleaning
- Uses regular expressions for efficient text manipulation
- Integrates with emoji library for emoji handling
- Designed for use with pandas DataFrames in a YouTube analysis pipeline

Dependencies:
- emoji: Converts emojis to text representations
- re: Regular expression operations for text cleaning

"""

import emoji
import re

def clean_text(text):
    """
    Clean and normalize input text for analysis.
    
    Processes a text string by converting emojis to their textual descriptions,
    removing URLs, retaining basic punctuation, and normalizing whitespace.
    
    Args:
        text (str): The input text to clean (e.g., a YouTube comment)
        
    Returns:
        str: Cleaned text, or empty string if input is not a string
    """
    if not isinstance(text, str):
        return ""
    text = emoji.demojize(text, delimiters=(" ", " "))  # Convert 😂 -> face_with_tears_of_joy
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)  # Remove URLs
    text = re.sub(r"[^A-Za-z0-9\s.,!?_:]", '', text)     # Keep basic punctuation and alphanumeric characters
    text = re.sub(r"\s+", ' ', text).strip()             # Normalize whitespace and strip
    return text
