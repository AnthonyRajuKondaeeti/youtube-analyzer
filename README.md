# YouTube Video Analyzer

This project is a Flask-based web application and Chrome extension for analyzing YouTube video transcripts and comments. It extracts video metadata, transcripts, and comments using YouTube APIs, performs sentiment and emotion analysis, extracts keywords, and generates visualizations. Users can interact via a web interface or a Chrome extension popup directly from YouTube video pages.

## Features

- **Transcript Extraction**: Fetches YouTube transcripts in multiple languages (English, Hindi, Telugu) using the YouTube Transcript API.
- **Comment Analysis**: Retrieves up to 300 comments and classifies sentiments (Positive, Neutral, Negative) with a RoBERTa model.
- **Emotion Analysis**: Detects emotions (e.g., joy, anger, sadness) in transcripts using a DistilRoBERTa model.
- **Keyword Extraction**: Identifies key terms in transcripts with YAKE.
- **Visualizations**: Creates:
  - Stacked area charts and heatmaps for emotion trends.
  - Pie charts for comment sentiment distribution.
- **Interactive Dashboard**: Displays transcript text, CSV tables, visualizations, and metadata (video title, channel name).
- **Chrome Extension**: Starts analysis from YouTube pages with a popup interface.
- **Asynchronous Processing**: Uses background tasks and status polling for a smooth user experience.

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- YouTube Data API key ([Google Cloud Console](https://console.cloud.google.com/))
- Git (optional, for cloning)

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/youtube-video-analyzer.git
   cd youtube-video-analyzer
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Example `requirements.txt`:

   ```
   flask==2.0.1
   flask-cors==3.0.10
   pandas==1.5.0
   transformers==4.20.0
   torch==1.12.0
   yake==0.4.8
   matplotlib==3.5.2
   seaborn==0.11.2
   google-api-python-client==2.50.0
   youtube-transcript-api==0.4.4
   emoji==2.0.0
   tqdm==4.64.0
   python-dotenv==0.20.0
   ```

4. **Configure API Key**:
   Create a `.env` file:

   ```plaintext
   API_KEY=your_youtube_api_key
   ```

5. **Run the Web App**:

   ```bash
   python app.py
   ```

   Access at `http://localhost:5000`.

6. **Install Chrome Extension**:
   - Open `chrome://extensions/` in Chrome.
   - Enable "Developer mode".
   - Click "Load unpacked" and select the `yt-extension` folder.

## Usage

### Web App

1. Open `http://localhost:5000` in a browser.
2. Enter a YouTube video URL and select a language (English, Hindi, Telugu).
3. Click "Analyze" to start processing.
4. View the results dashboard, including:
   - Full transcript with clickable timestamps.
   - Comment sentiment data in CSV tables.
   - Emotion charts (stacked area, heatmap) and sentiment pie chart.
   - Video title and channel name.
5. Outputs are saved in `static/data`:
   - `full_text.txt`: Transcript text.
   - `comments_with_sentiment.csv`: Sentiment-analyzed comments.
   - `transcript_emotion_keywords.csv`: Emotion-analyzed transcript.
   - `top_keywords_yake.csv`: Extracted keywords.
   - Visualization images (e.g., `emotion_stacked_area.png`, `sentiment_pie_chart.png`).

### Chrome Extension

1. Ensure the web app is running.
2. Open a YouTube video in Chrome.
3. Click the extension icon, select a language, and click "Start Analysis".
4. Wait for the results page to open in a new tab.

## Project Structure

```
youtube-video-analyzer/
│
├── static/                    # Static files (output data)
│   └── data/                  # CSVs, text, and images
├── templates/                 # HTML templates
│   ├── index.html            # Input form
│   ├── processing.html       # Processing status
│   ├── results.html          # Results dashboard
│   └── error.html            # Error page
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── youtube_api.py        # YouTube API interactions
│   ├── visualization.py      # Chart generation
│   ├── sentiment_analysis.py # Comment sentiment analysis
│   ├── preprocess.py         # Text cleaning
│   ├── keyword_transcript.py # Keyword extraction
│   ├── emotion_analysis.py   # Transcript emotion analysis
├── yt-extension/              # Chrome extension
│   ├── manifest.json         # Extension config
│   ├── popup.html            # Popup UI
│   ├── popup.js              # Popup logic
│   ├── icon.jpeg             # Icon (convert to PNG)
├── .env                       # API key
├── app.py                     # Flask app
├── main.py                    # Core processing
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## Dependencies

- `flask`, `flask-cors`: Web framework and CORS support
- `google-api-python-client`, `youtube-transcript-api`: YouTube APIs
- `transformers`, `torch`: Sentiment and emotion analysis
- `pandas`: Data handling
- `yake`: Keyword extraction
- `matplotlib`, `seaborn`: Visualizations
- `emoji`, `tqdm`, `python-dotenv`: Text processing and utilities

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Use clear code and test your changes.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/) for AI models.
- [YAKE](https://github.com/LIAAD/yake) for keyword extraction.
- YouTube APIs for data access.
- Inspired by the need to analyze YouTube video content and audience reactions.
