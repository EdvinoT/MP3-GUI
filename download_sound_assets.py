# download_sound_assets.py
import urllib.request
import os
import ssl

def download_premium_sound(url, destination_filename):
    print(f"Fetching {destination_filename}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        # FIX: Create an unverified SSL context to bypass the macOS certificate error
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=context) as response, open(destination_filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully saved to: {destination_filename}")
    except Exception as e:
        print(f"Could not download asset: {e}")

# High-quality audio paths
CLICK_URL = "https://actions.google.com/sounds/v1/interfaces/simple_click.ogg" 
SCROLL_URL = "https://actions.google.com/sounds/v1/interfaces/digital_clicks.ogg"

download_premium_sound(CLICK_URL, "click.ogg")
download_premium_sound(SCROLL_URL, "scroll.ogg")