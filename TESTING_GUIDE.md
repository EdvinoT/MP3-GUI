# Testing Guide - MP3 Player

## Quick Start (Testing on Mac)

### Step 1: Install test dependencies
```bash
pip install -r requirements-test.txt
```

### Step 2: Add test MP3 files
```bash
# Create tracks folder if it doesn't exist
mkdir -p tracks

# Copy some MP3s (or any audio file)
cp ~/Music/*.mp3 ./tracks/

# Or create a dummy audio file for testing
# Any MP3, WAV, or OGG file works
```

### Step 3: Run test
```bash
python3 test_player.py
```

### Step 4: Run the player
```bash
python3 mp3_player_compact.py
```

---

## What Works on Mac (Testing Mode)

✅ **Audio playback** - MP3 files will play through speakers
✅ **Volume control** - Set volume in code
✅ **Track management** - Load, skip, previous
✅ **All core logic** - Everything except hardware

❌ **GPIO buttons** - Not available on Mac
❌ **OLED display** - Not available on Mac
❌ **Bluetooth** - Different setup on Mac

---

## Requirements Files

### For Testing (Mac)
```bash
pip install -r requirements-test.txt
```

Installs:
- pygame (audio)
- Pillow (images)

### For Raspberry Pi
```bash
pip install -r requirements.txt
```

Installs everything + GPIO + OLED drivers

---

## Testing Checklist

- [ ] Run `pip install -r requirements-test.txt`
- [ ] Run `python3 test_player.py` (verify setup)
- [ ] Add MP3 files to `tracks/` folder
- [ ] Run `python3 mp3_player_compact.py`
- [ ] Check console output (should show tracks loaded)
- [ ] Press Ctrl+C to stop

---

## Common Test Issues

### Error: "No module named pygame"
**Fix:**
```bash
pip install pygame
```

### Error: "No module named PIL"
**Fix:**
```bash
pip install Pillow
```

### Error: "tracks folder not found"
**Fix:**
```bash
mkdir -p tracks
cp ~/Music/*.mp3 tracks/
```

### Error: "No tracks found"
**Fix:**
Verify MP3s are in `tracks/` folder:
```bash
ls -la tracks/
```

### Error: "RPi.GPIO not found"
**This is OK on Mac!** 
The code handles this automatically (testing mode).

---

## Test with Different Audio Formats

The code works with any format pygame supports:
- ✓ MP3
- ✓ WAV
- ✓ OGG
- ✓ FLAC

Just drop them in the `tracks/` folder.

---

## Monitoring Playback

During testing, the console shows:
```
=== MP3 Player Initialized ===
Platform: darwin
GPIO available: False
Display available: False
Tracks loaded: 5
================================

Playing: song_name.mp3
```

---

## On Raspberry Pi (Later)

Once you have the Pi + hardware:
```bash
pip install -r requirements.txt
python3 mp3_player_compact.py
```

Then everything works:
- GPIO buttons respond instantly
- OLED displays track info
- All hardware integrated

---

## Next Steps

1. ✅ Test on Mac with `test_player.py`
2. ✅ Verify audio playback works
3. ➡️ Order Raspberry Pi + OLED + buttons
4. ➡️ Assemble hardware
5. ➡️ Run on Pi (full functionality)

---

**Still having issues? Run `test_player.py` first - it will tell you exactly what's missing!**
