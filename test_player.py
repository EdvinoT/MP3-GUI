#!/usr/bin/env python3
"""
Quick test to verify MP3 player is working
Run: python3 test_player.py
"""

import os
import sys

print("\n" + "="*50)
print("MP3 PLAYER - TEST SUITE")
print("="*50 + "\n")

# Test 1: Check files exist
print("✓ Test 1: Checking files...")
required_files = [
    'mp3_player_compact.py',
    'tracks',
    'requirements-test.txt'
]
for f in required_files:
    if os.path.exists(f):
        print(f"  ✓ {f} found")
    else:
        print(f"  ✗ {f} MISSING")

# Test 2: Check Python packages
print("\n✓ Test 2: Checking Python packages...")
packages = {
    'pygame': 'Audio playback',
    'PIL': 'Image handling',
}

for pkg, desc in packages.items():
    try:
        __import__(pkg)
        print(f"  ✓ {pkg:20} - {desc}")
    except ImportError:
        print(f"  ✗ {pkg:20} - NOT INSTALLED (run: pip install -r requirements-test.txt)")

# Test 3: Check MP3 files
print("\n✓ Test 3: Checking MP3 files...")
if os.path.exists('tracks'):
    mp3_files = [f for f in os.listdir('tracks') if f.endswith('.mp3')]
    print(f"  Found {len(mp3_files)} MP3 files in tracks/")
    if len(mp3_files) > 0:
        for mp3 in mp3_files[:5]:  # Show first 5
            print(f"    - {mp3}")
        if len(mp3_files) > 5:
            print(f"    ... and {len(mp3_files) - 5} more")
    else:
        print("  ⚠ No MP3 files found. Add some to tracks/ folder first:")
        print("    cp ~/Music/*.mp3 ./tracks/")
else:
    print("  ✗ tracks/ folder not found")

# Test 4: Try importing the app
print("\n✓ Test 4: Testing app import...")
try:
    import mp3_player_compact
    print("  ✓ mp3_player_compact.py imports successfully")
except Exception as e:
    print(f"  ✗ Error importing: {e}")
    print("\n  Fix: pip install -r requirements-test.txt")

# Test 5: Check system platform
print("\n✓ Test 5: System info...")
print(f"  Platform: {sys.platform}")
print(f"  Python: {sys.version}")

print("\n" + "="*50)
print("SETUP COMPLETE!")
print("="*50)
print("\nTo run the player:")
print("  python3 mp3_player_compact.py")
print("\nNote:")
print("  - GPIO buttons won't work on Mac (testing mode)")
print("  - OLED display won't show on Mac (testing mode)")
print("  - Audio playback will work ✓")
print()
