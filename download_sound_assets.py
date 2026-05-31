# download_sound_assets.py
import urllib.request
import os
import ssl

def download_premium_sound(url, destination_filename):
    print(f"Fetching {destination_filename}...")
    try:
        # Standard browser headers to prevent basic security blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # Bypass macOS Python local issuer SSL certificate errors safely
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=context) as response, open(destination_filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully saved to: {destination_filename}")
    except Exception as e:
        print(f"Could not download asset: {e}")

# Stable, permanent open-source UI audio paths from Wikimedia Commons
CLICK_URL = "https://upload.wikimedia.org/wikipedia/commons/4/40/Mops_click.ogg"
SCROLL_URL = "https://upload.wikimedia.org/wikipedia/commons/c/ce/Xenon_Click.ogg"

download_premium_sound(CLICK_URL, "click.ogg")
download_premium_sound(SCROLL_URL, "scroll.ogg")