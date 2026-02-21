🖼️ AI Image Renamer

An intelligent Python tool that uses the Google Gemini AI to analyze your images and automatically rename them with descriptive, meaningful names.

No more IMG_20240101_1234.jpg. Get names like sunset_mountain_lake.jpg automatically.

✨ Features

AI Analysis: Uses Gemini 3 Flash to "see" your images and generate titles.

Batch Processing: Process an entire folder of images at once.

Customizable: Prepend/append text or add automatic date stamps.

Real-time Feedback: Includes a live terminal timer and progress indicator.

Secure: Uses environment variables for API keys to keep your credentials safe.

🚀 Getting Started

Prerequisites

Python 3.8+

A Google Gemini API Key (Get one for free at Google AI Studio)

Installation

Clone the repository

git clone [https://github.com/YOUR_USERNAME/ai-image-renamer.git](https://github.com/YOUR_USERNAME/ai-image-renamer.git)
cd ai-image-renamer


Install dependencies

pip install requests python-dotenv


Set up your API Key
Create a file named .env in the root directory and add your key:

GEMINI_API_KEY=your_actual_api_key_here


(The .env file is ignored by Git to keep your key private.)

💻 Usage

Run the script:

python ai_image_renamer.py


Follow the prompts to provide your folder path and optional naming preferences.

🛡️ Privacy & Security

This project uses a .gitignore file to ensure that sensitive information (like your API key) and local backup files are never uploaded to GitHub.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.