"""
YouTube Transcript Keyword Extraction Module

This Python module provides functionality for extracting keywords from YouTube video transcripts using the YAKE (Yet Another Keyword Extractor) algorithm. It processes a list of transcript segments, saves the full text, and outputs a ranked list of keywords with their importance scores.

Features:
- Unsupervised keyword extraction using YAKE
- Support for customizable n-gram sizes and number of keywords
- Saves full transcript text and keyword data to files
- Returns keyword data in a pandas DataFrame for further processing
- Robust handling of empty or invalid input

Architecture:
- Single-function module for keyword extraction
- Integrates YAKE for unsupervised keyword extraction
- Uses pandas for DataFrame creation and CSV output
- File-based storage for text and keyword data
- Designed for integration with a Flask-based YouTube analysis application

Dependencies:
- yake: YAKE keyword extraction library
- pandas: DataFrame creation and CSV handling
- matplotlib: Optional plotting library (for commented-out visualization)
- seaborn: Optional visualization styling (for commented-out visualization)
- os: File system operations for saving outputs

Author: Anonymous
Version: 1.0
"""

import yake
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def extract_keywords_yake(text_list, top_n=20, ngram=1, output_dir="data", visualize=False):
    """
    Extract keywords from a list of texts using YAKE.
    
    Processes a list of transcript segments to extract the top keywords, saves the full
    transcript text to a file, and outputs a DataFrame of keywords with their scores.
    
    Args:
        text_list (list): List of strings (e.g., transcript segments)
        top_n (int): Number of top keywords to extract (default: 20)
        ngram (int): Maximum n-gram size for keywords (default: 1 for unigrams)
        output_dir (str): Directory to save the full text and CSV output (default: "data")
        visualize (bool): Ignored in this implementation (no visualization included)
        
    Returns:
        pd.DataFrame: DataFrame with columns ["Keyword", "Score"] containing top keywords
                     and their importance scores, or empty DataFrame if input is empty
    """
    if not text_list:
        return pd.DataFrame(columns=["Keyword", "Score"])

    full_text = " ".join(text_list)
    # Save the full transcript text to a file
    text_path = os.path.join(output_dir, "full_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    # Initialize YAKE extractor with specified parameters
    kw_extractor = yake.KeywordExtractor(lan="en", n=ngram, top=top_n)
    keywords = kw_extractor.extract_keywords(full_text)

    # Convert keywords to DataFrame
    keyword_df = pd.DataFrame(keywords, columns=["Keyword", "Score"])
    output_path = os.path.join(output_dir, "top_keywords_yake.csv")
    keyword_df.to_csv(output_path, index=False)

    return keyword_df

# def extract_keywords_yake(texts, top_n=15, ngram=1, output_dir="data", visualize=True):
#     """
#     Alternative implementation of keyword extraction with visualization.
#     
#     Extracts keywords using YAKE and optionally generates a bar plot of the top keywords.
#     
#     Args:
#         texts (list): List of strings (e.g., transcript segments)
#         top_n (int): Number of top keywords to extract (default: 15)
#         ngram (int): Maximum n-gram size for keywords (default: 1 for unigrams)
#         output_dir (str): Directory to save CSV and optional PNG output (default: "data")
#         visualize (bool): Whether to generate a bar plot of keywords (default: True)
#         
#     Returns:
#         pd.DataFrame: DataFrame with columns ["keyword", "score"] containing top keywords
#                      and their rounded importance scores
#     """
#     text_full = " ".join(texts)
#     kw_extractor = yake.KeywordExtractor(n=ngram, top=top_n)
#     keywords = kw_extractor.extract_keywords(text_full)
# 
#     # Convert to DataFrame
#     keyword_df = pd.DataFrame(keywords, columns=["keyword", "score"])
#     keyword_df["score"] = keyword_df["score"].round(4)
# 
#     # Save to CSV
#     os.makedirs(output_dir, exist_ok=True)
#     csv_path = os.path.join(output_dir, "top_keywords_yake.csv")
#     keyword_df.to_csv(csv_path, index=False)
# 
#     # Optional Visualization
#     if visualize:
#         plt.figure(figsize=(10, 6))
#         sns.barplot(data=keyword_df.sort_values("score", ascending=True), 
#                     x="score", y="keyword", palette="mako")
#         plt.title("Top Keywords (YAKE)")
#         plt.xlabel("Importance (Lower is Better)")
#         plt.ylabel("Keyword")
#         plt.tight_layout()
#         plt.savefig(os.path.join(output_dir, "top_keywords_yake.png"))
#         plt.close()
# 
#     return keyword_df