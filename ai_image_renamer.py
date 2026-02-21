import os
import base64
import re
import time
import sys
import threading
from datetime import datetime
from pathlib import Path
import requests
# Import dotenv to read the .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Configuration ---
# 1. This now pulls from your .env file automatically
API_KEY = os.getenv("GEMINI_API_KEY", "") 

# Using the current 2026 stable-preview model
MODEL_NAME = "gemini-3-flash-preview"

def get_api_url():
    return f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def encode_image(image_path):
    """Encodes an image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def sanitize_filename(name, max_length=200):
    """Sanitizes the AI's suggestion for OS compatibility."""
    clean_name = re.sub(r'[\\/:*?"<>|]', '', name)
    clean_name = re.sub(r'\s+', '_', clean_name)
    clean_name = clean_name.encode("ascii", "ignore").decode("ascii")
    clean_name = clean_name.strip(". _")
    return clean_name[:max_length]

class ProgressIndicator:
    """A terminal progress indicator with a timer."""
    def __init__(self, message="Processing"):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None
        self.start_time = 0

    def _animate(self):
        chars = [".  ", ".. ", "...", " ..", "  .", "   "]
        idx = 0
        while not self.stop_event.is_set():
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"\r  {self.message} {chars[idx % len(chars)]} ({elapsed:.1f}s)")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.3)

    def start(self):
        self.start_time = time.time()
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self, success=True, error_msg=None):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        elapsed = time.time() - self.start_time
        status = "Done" if success else "Failed"
        sys.stdout.write(f"\r  {self.message} -> {status}! ({elapsed:.1f}s)\n")
        if error_msg:
            sys.stdout.write(f"    Reason: {error_msg}\n")
        sys.stdout.flush()

def call_gemini_with_retry(prompt, base64_image):
    """Calls Gemini API and returns (result, error_message)."""
    if not API_KEY:
        return None, "API_KEY not found. Check your .env file or environment variables."

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/png", "data": base64_image}}
            ]
        }]
    }

    retries = 3
    last_error = "Unknown error"
    
    for i in range(retries):
        try:
            response = requests.post(get_api_url(), json=payload, timeout=45)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text'].strip(), None
            else:
                error_data = response.json()
                last_error = error_data.get('error', {}).get('message', f"Status {response.status_code}")
        except Exception as e:
            last_error = str(e)
        
        if i < retries - 1:
            time.sleep(2**i)
            
    return None, last_error

def main():
    print("\033[1m--- AI Image Renamer ---\033[0m")
    if not API_KEY:
        print("Error: API Key not found. Please ensure you have a .env file with GEMINI_API_KEY=your_key")
        return

    folder_input = input("Enter the path to the folder: ").strip().strip('"')
    path = Path(folder_input)
    
    if not path.is_dir():
        print(f"Error: '{path}' is not a valid directory.")
        return

    prefix = input("Enter text to PREPEND (leave blank): ").strip()
    suffix = input("Enter text to APPEND (leave blank): ").strip()
    add_date = input("Add date stamp? (y/n): ").lower().startswith('y')
    
    date_string = datetime.now().strftime("_%Y-%m-%d") if add_date else ""
    supported = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    files = [f for f in path.iterdir() if f.suffix.lower() in supported]
    
    if not files:
        print("No supported images found.")
        return

    total = len(files)
    print(f"Analyzing {total} images...")

    prompt = (
        "Analyze this image and provide a unique and concise filename (1-3 words). "
        "Use lowercase and underscores. Output ONLY the filename, nothing else."
    )

    success_count = 0
    for idx, img_path in enumerate(files, 1):
        print(f"\n[{idx}/{total}] {img_path.name}")
        indicator = ProgressIndicator("AI analysis in progress")
        indicator.start()
        
        try:
            b64_data = encode_image(img_path)
            ai_suggestion, error = call_gemini_with_retry(prompt, b64_data)
            
            if error:
                indicator.stop(success=False, error_msg=error)
                continue

            indicator.stop(success=True)
            clean_suggestion = sanitize_filename(ai_suggestion)
            
            parts = [p for p in [prefix, clean_suggestion, suffix] if p]
            base_new_name = "_".join(parts)
            final_filename = f"{base_new_name}{date_string}{img_path.suffix.lower()}"
            
            new_file_path = img_path.parent / final_filename
            counter = 1
            while new_file_path.exists():
                final_filename = f"{base_new_name}{date_string}_{counter}{img_path.suffix.lower()}"
                new_file_path = img_path.parent / final_filename
                counter += 1
            
            img_path.rename(new_file_path)
            print(f"    Renamed to: {final_filename}")
            success_count += 1
            
        except Exception as e:
            indicator.stop(success=False, error_msg=str(e))

    print(f"\nSuccess! Renamed {success_count} of {total} images.")

if __name__ == "__main__":
    main()