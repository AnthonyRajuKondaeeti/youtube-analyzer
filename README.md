# YouTube Video Transcript and Comment Analysis

This project is a Flask-based web application that analyzes YouTube video transcripts and comments to provide insights into sentiment, emotions, and key topics. It extracts video metadata, comments, and transcripts using the YouTube API, performs sentiment and emotion analysis, extracts keywords, and generates visualizations to display results in an interactive dashboard.

## Features
- **Transcript Extraction**: Fetches YouTube video transcripts with multi-language support using the YouTube Transcript API.
- **Comment Analysis**: Retrieves up to 300 comments and performs sentiment analysis (positive, neutral, negative) using a RoBERTa-based model.
- **Emotion Analysis**: Analyzes transcript segments for emotions (e.g., joy, anger, sadness) using a DistilRoBERTa-based model.
- **Keyword Extraction**: Identifies top keywords in transcripts using YAKE (Yet Another Keyword Extractor).
- **Visualizations**: Generates:
  - Stacked area charts and heatmaps for emotion trends over time.
  - Pie charts for comment sentiment distribution.
- **Interactive Dashboard**: Displays results including transcript text, CSV tables, visualizations, and video metadata (title, channel name).
- **Asynchronous Processing**: Uses threading for non-blocking analysis with real-time status updates via AJAX.
- **Robust Error Handling**: Manages API errors, missing transcripts, and invalid inputs with comprehensive logging.

## Installation

### Prerequisites
- Python 3.8 or higher
- A YouTube Data API key (obtain from [Google Cloud Console](https://console.cloud.google.com/))
- Git (optional, for cloning the repository)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/youtube-analysis.git
   cd youtube-analysis
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Create a `.env` file in the project root.
   - Add your YouTube API key:
     ```plaintext
     API_KEY=your_youtube_api_key
     ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   - The application will start at `http://localhost:5000`.

## Usage
1. **Access the Web Interface**:
   - Open `http://localhost:5000` in your browser.
   - Enter a YouTube video URL and select a transcript language (default: English).

2. **Analyze a Video**:
   - Submit the form to start processing.
   - The application will fetch comments, transcripts, and metadata, then perform sentiment analysis, emotion analysis, and keyword extraction.
   - A processing page will display until analysis is complete.

3. **View Results**:
   - Once processing is done, you’ll be redirected to a results dashboard showing:
     - Full transcript text with clickable timestamps.
     - CSV tables of comment sentiments and transcript emotions.
     - Visualizations (emotion stacked area chart, heatmap, sentiment pie chart).
     - Video title and channel name.

4. **Output Files**:
   - Results are saved in the `static/data` directory, including:
     - `full_text.txt`: Full transcript text.
     - `comments_with_sentiment.csv`: Comments with sentiment labels and confidence scores.
     - `transcript_emotion_keywords.csv`: Transcript with emotion labels and scores.
     - `top_keywords_yake.csv`: Top keywords extracted from the transcript.
     - Visualization images (e.g., `emotion_stacked_area.png`, `sentiment_pie_chart.png`).

## Project Structure
```
youtube-analysis/
│
├── static/                    # Static files (CSS, JS, data outputs)
│   ├── data/                  # Output directory for CSVs, text, and images
│   ├── css/                   # CSS styles
│   └── js/                    # JavaScript for frontend
│
├── templates/                 # HTML templates for Flask
│   ├── processing.html        # Processing status page
│   └── results.html           # Results dashboard
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── emotion_analysis.py    # Emotion analysis using DistilRoBERTa
│   ├── keyword_transcript.py  # Keyword extraction using YAKE
│   ├── preprocess.py          # Text preprocessing
│   ├── sentiment_analysis.py  # Sentiment analysis using RoBERTa
│   ├── visualization.py       # Visualization generation
│   └── youtube_api.py         # YouTube API interactions
│
├── .env                       # Environment variables (API key)
├── app.py                     # Main Flask application
├── main.py                    # Core processing logic
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Dependencies
Key dependencies (see `requirements.txt` for the full list):
- `flask`: Web framework for the application
- `flask-cors`: Cross-origin resource sharing support
- `google-api-python-client`: YouTube Data API interactions
- `youtube-transcript-api`: Transcript extraction
- `transformers`: Sentiment and emotion analysis models
- `pandas`: Data manipulation
- `yake`: Keyword extraction
- `matplotlib`, `seaborn`: Visualization generation
- `python-dotenv`: Environment variable management
- `tqdm`: Progress bars for processing

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure your code follows PEP 8 style guidelines and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Built with [Flask](https://flask.palletsprojects.com/), [Hugging Face Transformers](https://huggingface.co/), and [YAKE](https://github.com/LIAAD/yake).
- Inspired by the need to analyze YouTube video content and audience reactions.
