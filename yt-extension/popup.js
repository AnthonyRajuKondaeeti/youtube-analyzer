/*
YouTube Video Analyzer Chrome Extension Popup Script

This JavaScript file powers the popup interface of a Chrome extension for the YouTube Video Analyzer. It handles the "Start Analysis" button click, retrieves the active tab's URL, validates it as a YouTube video, and sends a POST request to a local server (http://127.0.0.1:5000) with the video URL and selected language. The script displays a loading spinner during processing, polls the server for status updates every 3 seconds, and opens the results page in a new tab upon completion, auto-closing the popup. Error handling ensures user feedback for invalid URLs, server issues, or connection failures.

Features:
- Retrieves active tab URL and validates it as a YouTube video
- Sends video URL and language to local server via POST request
- Polls server for processing status
- Displays loading spinner and status messages
- Opens results page in new tab and closes popup upon completion
- Handles errors with user-friendly messages

Dependencies:
- Chrome Extension API: For tab querying and tab creation
- Fetch API: For server communication
- popup.html: For DOM elements (button, select, status, loading)

*/

// Add click event listener to the "Start Analysis" button
document.getElementById("analyzeBtn").addEventListener("click", async () => {
  // Query the active tab in the current window
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Get the tab's URL and selected language from the dropdown
  const videoUrl = tab.url;
  const language = document.getElementById("language").value;

  // Validate if the URL is a YouTube video page
  if (!videoUrl.includes("youtube.com/watch")) {
    document.getElementById("status").textContent = "Not a valid YouTube video.";
    return;
  }

  // Clear status message and show loading spinner
  document.getElementById("status").textContent = "";
  document.getElementById("loading").style.display = "block";

  try {
    // Send POST request to the local server with video URL and language
    const response = await fetch("http://127.0.0.1:5000/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        video_url: videoUrl,
        language: language
      })
    });

    // Check if the server responded successfully
    if (response.ok) {
      // Update status to indicate processing has started
      document.getElementById("status").textContent = "Processing started...";

      // Define function to poll server for processing status
      const pollStatus = async () => {
        try {
          // Fetch status from the server
          const statusResponse = await fetch("http://127.0.0.1:5000/check_status");
          const statusData = await statusResponse.json();

          // Check if processing is complete
          if (statusData.done) {
            // Hide loading spinner
            document.getElementById("loading").style.display = "none";
            // Open results page in a new tab and close popup
            chrome.tabs.create({ url: "http://127.0.0.1:5000/results" }, () => {
              window.close(); // Auto-close popup
            });
          } else {
            // Poll again after 3 seconds if not done
            setTimeout(pollStatus, 3000);
          }
        } catch (err) {
          // Log polling error and update UI
          console.error("Polling error:", err);
          document.getElementById("status").textContent = "Failed to check processing status.";
          document.getElementById("loading").style.display = "none";
        }
      };

      // Start polling for status
      pollStatus();

    } else {
      // Handle server error response
      document.getElementById("status").textContent = "Server error.";
      document.getElementById("loading").style.display = "none";
    }

  } catch (err) {
    // Handle connection or other errors
    console.error(err);
    document.getElementById("status").textContent = "Connection failed.";
    document.getElementById("loading").style.display = "none";
  }
});
