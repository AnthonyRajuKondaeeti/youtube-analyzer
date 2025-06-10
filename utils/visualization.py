"""
YouTube Video Analysis Visualization Module

This Python module provides functions to generate visualizations for YouTube video transcript and comment analysis. It creates charts to display emotion trends and sentiment distributions, supporting the visualization of analytical insights in a web-based application.

Features:
- Generation of stacked area charts for emotion trends over time
- Creation of heatmaps to show emotion intensity across video duration
- Pie chart visualization of comment sentiment distribution
- Non-interactive Matplotlib backend for server-side rendering
- Robust file handling for saving visualization outputs

Architecture:
- Modular design with functions for specific visualization types
- Uses Matplotlib and Seaborn for plotting
- Integrates with Flask application for displaying visualizations
- File-based output for images (PNG, potentially GIF for animations)
- Error handling for missing data and invalid inputs

Dependencies:
- matplotlib: Core plotting library with non-interactive Agg backend
- seaborn: Enhanced visualization for heatmaps and color palettes
- pandas: Data manipulation for DataFrame processing
- os: File system operations for saving outputs
- math: Mathematical constants for potential radar chart calculations
- bar_chart_race: Optional dependency for animated bar chart races

"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from math import pi
import bar_chart_race as bcr
import os

# def plot_emotion_trend_scatter(df, color_map, output_dir):
#     """
#     Plot a scatter chart of emotions over transcript time.
#     
#     Creates a scatter plot showing the occurrence of emotions at specific timestamps.
#     
#     Args:
#         df (pd.DataFrame): DataFrame with transcript data and emotion labels
#         color_map (dict): Mapping of emotions to colors for plotting
#         output_dir (str): Directory to save the output PNG file
#     """
#     plt.figure(figsize=(14, 6))
#     for emotion in df["emotion"].unique():
#         mask = df["emotion"] == emotion
#         plt.scatter(df.loc[mask, "start"], [emotion]*mask.sum(), label=emotion, alpha=0.7, color=color_map.get(emotion, 'black'))
#     plt.xlabel("Time (seconds)")
#     plt.ylabel("Emotion")
#     plt.title("Emotion Trend Over Transcript Time")
#     plt.legend(title="Emotion", bbox_to_anchor=(1.05, 1))
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig(os.path.join(output_dir, "emotion_trend_scatter.png"))
#     plt.close()

def plot_emotion_stacked_area(df, output_dir):
    """
    Plot a stacked area chart of emotions over time.
    
    Groups transcript data into 30-second bins and visualizes emotion counts
    as a stacked area chart to show trends over the video duration.
    
    Args:
        df (pd.DataFrame): DataFrame with transcript data, including 'start' and 'emotion' columns
        output_dir (str): Directory to save the output PNG file
    """
    df["time_bin"] = (df["start"] // 30) * 30
    emotion_counts = df.groupby(["time_bin", "emotion"]).size().unstack(fill_value=0)
    
    ax = emotion_counts.plot.area(figsize=(16, 6), colormap='tab10', alpha=0.8)
    plt.title("Stacked Area Chart of Emotions Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Emotion Count")
    plt.legend(title="Emotion", bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space on right for legend
    
    # Save with tight layout so labels are not chopped
    plt.savefig(os.path.join(output_dir, "emotion_stacked_area.png"), bbox_inches='tight')
    plt.close()

def plot_emotion_heatmap(df, output_dir):
    """
    Plot a heatmap of emotion intensity over time.
    
    Groups transcript data into 30-second bins and creates a heatmap to show
    the distribution and intensity of emotions across the video.
    
    Args:
        df (pd.DataFrame): DataFrame with transcript data, including 'start' and 'emotion' columns
        output_dir (str): Directory to save the output PNG file
    """
    df["time_bin"] = (df["start"] // 30) * 30
    emotion_counts = df.groupby(["time_bin", "emotion"]).size().unstack(fill_value=0)
    plt.figure(figsize=(14, 6))
    sns.heatmap(emotion_counts.T, cmap="YlOrRd", annot=False, cbar=True)
    plt.title("Emotion Heatmap Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Emotion")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "emotion_heatmap.png"))
    plt.close()

# def plot_sentiment_distribution(df, output_dir):
#     """
#     Plot a bar chart showing the distribution of sentiment labels.
#     
#     Creates a bar chart to visualize the count of positive, neutral, and negative comments.
#     
#     Args:
#         df (pd.DataFrame): DataFrame with comment data and 'sentiment' column
#         output_dir (str): Directory to save the output PNG file
#         
#     Raises:
#         ValueError: If 'sentiment' column is missing
#     """
#     if "sentiment" not in df.columns:
#         raise ValueError("Missing 'sentiment' column in DataFrame")
#     
#     print(df['sentiment'].value_counts(dropna=False))
#     
#     plt.figure(figsize=(8, 5))
#     sns.countplot(data=df, x='sentiment', hue='sentiment', palette='pastel', order=['positive', 'neutral', 'negative'], legend=False)
#     plt.title("Sentiment Distribution of YouTube Comments")
#     plt.xlabel("Sentiment")
#     plt.ylabel("Number of Comments")
#     plt.tight_layout()
#     output_path = os.path.join(output_dir, "sentiment_distribution.png")
#     plt.savefig(output_path)
#     plt.close()

def plot_sentiment_distribution(df, output_dir):
    """
    Plot a pie chart showing the distribution of sentiment labels.
    
    Creates a pie chart to visualize the proportion of positive, neutral, and negative comments.
    
    Args:
        df (pd.DataFrame): DataFrame with comment data and 'sentiment' column
        output_dir (str): Directory to save the output PNG file
        
    Raises:
        ValueError: If 'sentiment' column is missing
    """
    if "sentiment" not in df.columns:
        raise ValueError("Missing 'sentiment' column in DataFrame")

    # Normalize sentiment case
    df['sentiment'] = df['sentiment'].str.lower().str.strip()

    sentiment_counts = df['sentiment'].value_counts()
    
    plt.figure(figsize=(6, 6))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    plt.title("Comments Sentiment Distribution (Pie Chart)")
    plt.tight_layout()
    output_path = os.path.join(output_dir, "sentiment_pie_chart.png")
    plt.savefig(output_path)
    plt.close()

# def plot_emotion_radar(df, start_sec=300, end_sec=450, color_map=None, output_dir="static/data"):
#     """
#     Plot a radar chart for emotion distribution in a time range.
#     
#     Creates a radar chart to show the distribution of emotions within a specified
#     time range of the transcript.
#     
#     Args:
#         df (pd.DataFrame): DataFrame with transcript data and 'emotion' column
#         start_sec (int): Start time in seconds for the snapshot
#         end_sec (int): End time in seconds for the snapshot
#         color_map (dict, optional): Mapping of emotions to colors
#         output_dir (str): Directory to save the output PNG file
#     """
#     snapshot = df[df["start"].between(start_sec, end_sec)]
#     emotion_counts = snapshot["emotion"].value_counts()
#     if color_map:
#         emotion_counts = emotion_counts.reindex(color_map.keys(), fill_value=0)
#     categories = list(emotion_counts.index)
#     values = emotion_counts.tolist() + [emotion_counts.tolist()[0]]
#     angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))] + [0]
#     plt.figure(figsize=(6, 6))
#     ax = plt.subplot(111, polar=True)
#     plt.xticks(angles[:-1], categories)
#     ax.plot(angles, values, linewidth=1, linestyle='solid')
#     ax.fill(angles, values, alpha=0.3)
#     plt.title(f"Emotion Distribution Snapshot ({start_sec}-{end_sec}s)")
#     plt.savefig(os.path.join(output_dir, f"emotion_radar_{start_sec}_{end_sec}.png"))
#     plt.close()

# def generate_emotion_bar_chart_race(df, filename="static/data/emotion_bar_race.gif"):
#     """
#     Generate an animated bar chart race for emotion trends.
#     
#     Creates an animated GIF showing the evolution of emotion counts over time
#     using 30-second bins.
#     
#     Args:
#         df (pd.DataFrame): DataFrame with transcript data and 'emotion' column
#         filename (str): Path to save the output GIF file
#     """
#     df["time_bin"] = (df["start"] // 30) * 30
#     binned_df = df.groupby(["time_bin", "emotion"]).size().unstack(fill_value=0)
# 
#     os.makedirs(os.path.dirname(filename), exist_ok=True)
# 
#     bcr.bar_chart_race(
#     df=binned_df,
#     filename=filename,
#     orientation='h',
#     sort='desc',
#     n_bars=seven,
#     fixed_order=False,
#     fixed_max=True,
#     steps_per_period=20,
#     interpolate_period=True,
#     period_length=1000,
#     title='Emotion Evolution Over Time',
#     bar_size=0.95,
#     period_label={'x': .99, 'y': .25, 'ha': 'right', 'va': 'center'},
#     figsize=(8, 6),
#     cmap='Set2'
# )
