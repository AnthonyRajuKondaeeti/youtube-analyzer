"""
YouTube Video Transcript Analysis Web Application

This Flask web application enables users to analyze YouTube video transcripts by extracting them, performing analytical computations, and generating visualizations. It provides a user-friendly interface to submit video URLs, monitor processing, and view results.

Features:
- Extraction of YouTube video transcripts with multi-language support
- Asynchronous background processing for efficient handling of analysis tasks
- Real-time status updates via AJAX polling
- Results dashboard displaying:
  * Full transcript text
  * Analytical data in CSV tables
  * Visualization images (e.g., charts, graphs)
  * Video metadata (title and channel name)

Architecture:
- Flask web framework with CORS for cross-origin request support
- Threading for non-blocking background processing
- File-based storage for generated CSV, image, and text files
- HTML template rendering for dynamic user interfaces

Dependencies:
- Flask: Web framework for routing and request handling
- Flask-CORS: Enables cross-origin resource sharing
- pandas: Handles CSV data processing and manipulation
- Custom modules: main.py (transcript extraction), visualization generation

"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import os
from main import main, generate_all_visualizations, generate_sentiment_visualizations
import pandas as pd
from threading import Thread

# Initialize Flask application with CORS support
app = Flask(__name__)
CORS(app)

# Configuration
app.config["UPLOAD_FOLDER"] = "static/data"  # Directory for storing generated files



# Global variables for tracking processing state and video metadata
processing_done = False
video_title = ""
channel_name = ""

def background_task(video_url, language):
    """
    Background processing function for video transcript analysis.
    
    Executes in a separate thread to handle time-intensive tasks without blocking
    the main Flask application.
    
    Args:
        video_url (str): YouTube video URL to analyze
        language (str): Language code for transcript extraction (e.g., 'en', 'es')
        
    Global Variables Modified:
        processing_done (bool): Set to True upon completion
        video_title (str): Stores the extracted video title
        channel_name (str): Stores the extracted channel name
    """
    global processing_done, video_title, channel_name
    
    try:
        # Extract transcript and metadata
        comments_df, transcript_df, video_title, channel_name = main(video_url, language=language)
        
        # Generate visualizations and save to output directory
        generate_all_visualizations(transcript_df, output_dir=app.config["UPLOAD_FOLDER"])
        generate_sentiment_visualizations(comments_df, output_dir=app.config["UPLOAD_FOLDER"])
        # Mark processing as complete
        processing_done = True
    
    except Exception as e:
        # Log errors and complete processing to prevent hanging
        print(f"Error in background processing: {str(e)}")
        processing_done = True

@app.route("/", methods=["POST"])
def analyze():
    """
    Endpoint to initiate video transcript analysis.
    
    Handles POST requests with a YouTube video URL and optional language parameter,
    starting a background thread for processing.
    
    Form Parameters:
        video_url (str, required): YouTube video URL
        language (str, optional): Language code for transcript (defaults to 'en')
        
    Returns:
        str: Success message with HTTP 200, or error with HTTP 400 if URL is missing
    """
    global processing_done
    
    # Reset processing state for new analysis
    processing_done = False

    # Extract form data
    video_url = request.form.get("video_url")
    language = request.form.get("language", "en")

    # Validate input
    if not video_url:
        return "Missing video_url in POST request", 400

    # Start background processing thread
    thread = Thread(target=background_task, args=(video_url, language))
    thread.daemon = True  # Ensure thread terminates with app
    thread.start()

    return "Processing started", 200

@app.route("/processing")
def processing():
    """
    Processing status page endpoint.
    
    Displays a loading page during analysis and redirects to results upon completion.
    
    Returns:
        Response: Redirect to results if processing is done, otherwise processing template
    """
    if processing_done:
        return redirect(url_for("results"))
    return render_template("processing.html")

@app.route("/check_status")
def check_status():
    """
    AJAX endpoint for checking processing status.
    
    Provides real-time updates for frontend polling to monitor analysis completion.
    
    Returns:
        JSON: Dictionary with 'done' key indicating processing status
    """
    return jsonify({"done": processing_done})


@app.route('/results')
def results():
    """
    Results dashboard endpoint.
    
    Renders a page with analysis results, including transcript, CSV data tables,
    visualization images, and video metadata. Processes generated files for display.
    
    File Processing:
        - CSV: Loaded, cleaned (e.g., remove 'cleaned_comment'), and formatted
        - Images: Collected for rendering
        - Text: Read for transcript display
        
    Returns:
        str: Rendered HTML template with analysis results
    """
    data_dir = app.config["UPLOAD_FOLDER"]
    
    # Initialize data structures
    all_csv_data = {}
    csv_filenames = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    image_filenames = [f for f in os.listdir(data_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    txt_filenames = [f for f in os.listdir(data_dir) if f.endswith('.txt')]

    # Load transcript from first text file, if available
    full_text = "No transcript available."
    if txt_filenames:
        txt_path = os.path.join(data_dir, txt_filenames[0])
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except Exception as e:
            print(f"Error reading transcript file: {str(e)}")
            full_text = "Error loading transcript."

    # Process CSV files
    for filename in csv_filenames:
        csv_path = os.path.join(data_dir, filename)
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)

                # Remove 'cleaned_comment' column if present
                columns_to_remove = ['cleaned_comment']
                for col in columns_to_remove:
                    if col in df.columns:
                        df = df.drop(columns=[col])

                # Round numeric columns for display
                numeric_columns = df.select_dtypes(include=['number']).columns
                df[numeric_columns] = df[numeric_columns].round(2)

                # Format data for template
                headers = list(df.columns)
                rows = df.values.tolist()
                all_csv_data[filename] = [headers] + rows
                
            except Exception as e:
                print(f"Error processing CSV file {filename}: {str(e)}")
                all_csv_data[filename] = [["Error"], [f"Failed to load {filename}"]]

    # Render results page with all data
    return render_template(
        'results.html',
        full_text=full_text,
        csv_data=all_csv_data,
        images=image_filenames,
        video_title=globals().get('video_title', 'Unknown Video'),
        channel_name=globals().get('channel_name', 'Unknown Channel')
    )


if __name__ == "__main__":
    """
    Application entry point.
    
    Starts the Flask development server in debug mode. For production, use a
    WSGI server like Gunicorn or uWSGI.
    """
    # Create upload directory if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Run development server
    app.run(debug=True)
