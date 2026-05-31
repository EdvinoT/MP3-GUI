# Raspberry Pi MP3 Player - Complete Hardware & Software Specs

## 🎵 CORE HARDWARE

### Main Components
| Component | Spec | Cost | Notes |
|-----------|------|------|-------|
| **SBC** | Raspberry Pi 4 (2GB RAM) | $45 | Best balance for GUI + audio |
| **Storage** | 32GB MicroSD Card (Class 10, U3) | $10 | Holds ~6,000+ MP3s |
| **Power** | 5V/3A USB-C PSU | $12 | Official or quality clone |
| **Case** | Aluminum Pi 4 Case w/ cooling | $15 | Prevents thermal throttling |
| **Audio Out** | 3.5mm Audio Jack (onboard) | Built-in | Use directly or via adapter |

**Subtotal: ~$82**

---

## 🖥️ DISPLAY OPTIONS (Choose ONE)

### Option A: 7" Touchscreen (RECOMMENDED)
- **Model:** Raspberry Pi 7" Touch Display
- **Resolution:** 800x480
- **Interface:** DSI connector
- **Cost:** $50-60
- **Pros:** Good size, touch controls, easy setup
- **Cons:** Uses both GPIO power pins

### Option B: 3.5" Touchscreen (COMPACT)
- **Model:** 3.5" TFT LCD Touch (Waveshare/Elecrow)
- **Resolution:** 480x320
- **Interface:** SPI + GPIO
- **Cost:** $25-35
- **Pros:** Fits in palm, room for buttons
- **Cons:** Smaller text, more crowded

### Option C: 2.42" OLED (RETRO/MINIMAL)
- **Model:** 2.42" SSD1306 I2C OLED
- **Resolution:** 128x64
- **Interface:** I2C
- **Cost:** $15-20
- **Pros:** Low power, crisp display, retro iPod vibe
- **Cons:** Tiny, needs text optimization

**Display Choice:** Go with **7" Touchscreen** for best UX

---

## 🔌 AUDIO HARDWARE

### Wired Headphones (No extra hardware needed)
- Use Pi's built-in 3.5mm jack
- Audio quality: Acceptable (basic DAC)

### Wireless Headphones
- Use Pi's Bluetooth 5.0 (built-in on Pi 4)
- Pairing via settings

### Better Audio Quality (Optional)
- **USB DAC:** Behringer UCA202 (~$30) - external DAC
- **HAT Audio:** IQaudio DAC+ (~$40) - stackable
- **Benefit:** Better audio quality, lower noise

---

## 🎛️ PHYSICAL BUTTONS (GPIO - Optional but Recommended)

### Button Setup
Connect to GPIO pins:
```
GPIO 17 → Play/Pause Button
GPIO 27 → Next Track Button
GPIO 22 → Previous Track Button
GPIO 23 → Volume Up Button
GPIO 24 → Volume Down Button
GND → Other side of all buttons
```

### Parts Needed Per Button
- Push button switch (momentary) - $1 each
- 10kΩ resistor - $0.10 each
- Jumper wires
- **Total for 5 buttons:** ~$10

### Wiring Diagram
```
[Button] ──→ [GPIO Pin]
   │
   └──→ [10kΩ Resistor] ──→ [GND]
```

---

## 📦 COMPLETE SHOPPING LIST

### Essential
- [ ] Raspberry Pi 4 (2GB) - $45
- [ ] 7" Touchscreen Display - $55
- [ ] 32GB MicroSD Card - $10
- [ ] 5V/3A USB-C PSU - $12
- [ ] Aluminum case with heatsink - $15
- [ ] MicroHDMI to HDMI cable (for Pi 4) - $5
- [ ] DSI ribbon cable for display - $3

**Subtotal: $145**

### Optional (Recommended)
- [ ] 5x Push buttons - $5
- [ ] 5x 10kΩ resistors - $1
- [ ] Jumper wires (pack) - $3
- [ ] Breadboard (for prototyping) - $3

**Optional Subtotal: $12**

### Audio Enhancement (Optional)
- [ ] USB DAC (Behringer) - $30
- OR
- [ ] IQaudio DAC+ HAT - $40

---

## 💾 SOFTWARE REQUIREMENTS

### OS
- **Raspberry Pi OS Lite** (headless, lighter) - **RECOMMENDED**
- Or **Raspberry Pi OS Desktop** (GUI available as fallback)
- Download: https://www.raspberrypi.com/software/

### Python Packages
```bash
# Core
pygame==2.1.3          # Audio playback
customtkinter==5.2.0   # GUI framework
Pillow==10.0.0         # Image handling

# Optional
RPi.GPIO==0.7.0        # Physical button control (GPIO)
pyaudio==0.2.13        # Advanced audio (optional)
```

### Installation
```bash
pip install pygame customtkinter Pillow RPi.GPIO
```

---

## ⚙️ SOFTWARE SETUP ON PI

### 1. Fresh Install
```bash
# Flash Raspberry Pi OS Lite to MicroSD
# Boot Pi and run:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev libsdl2-mixer-2.0-0
```

### 2. Clone/Copy Your App
```bash
# Copy main.py, background.png, and any MP3s to Pi
scp -r ~/MP3-GUI pi@raspberrypi.local:~/
```

### 3. Install Dependencies
```bash
cd ~/MP3-GUI
pip install -r requirements.txt
```

### 4. Autostart on Boot (Optional)
```bash
# Create systemd service
sudo nano /etc/systemd/system/mp3player.service
```

Paste:
```ini
[Unit]
Description=MP3 Player
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/MP3-GUI
ExecStart=/usr/bin/python3 /home/pi/MP3-GUI/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable mp3player.service
sudo systemctl start mp3player.service
```

---

## 🔧 GPIO BUTTON IMPLEMENTATION

### Python GPIO Code (to add to main.py)
```python
import RPi.GPIO as GPIO
from threading import Thread

class GPIOButtons:
    def __init__(self, app):
        self.app = app
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.button_pins = {
            17: self.app.toggle_play,      # Play/Pause
            27: self.app.next_track,       # Next
            22: self.app.prev_track,       # Previous
            23: self.app.volume_up,        # Volume+
            24: self.app.volume_down,      # Volume-
        }
        
        # Setup each button
        for pin, callback in self.button_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, 
                                callback=lambda x, cb=callback: cb(), 
                                bouncetime=300)
    
    def cleanup(self):
        GPIO.cleanup()
```

---

## 📏 PHYSICAL DIMENSIONS & CASE

### Recommended Case Setup
- **Aluminum case** for Pi 4: ~150mm x 85mm x 32mm
- **With 7" display:** Mount on adjustable arm/stand
- **With buttons:** Mount on front panel using 3D-printed bracket
- **Total device size:** ~250mm x 180mm x 50mm (roughly iPhone-sized)

---

## 🔋 POWER CONSIDERATIONS

### Power Draw
- Pi 4 (idle): ~2-3W
- Pi 4 (full load): ~10-15W
- Display (7"): ~1-2W
- USB DAC (if used): ~0.5W

**Total: 3-5W typical, 12-18W peak**

### Battery Option (Optional)
- **UPS Module:** Waveshare 2000mAh (~$30)
- **Runtime:** ~2-3 hours of continuous playback
- Good for portable version

---

## 📊 PERFORMANCE EXPECTATIONS

| Task | Performance | Notes |
|------|-------------|-------|
| Boot time | 20-30 seconds | From power on to UI |
| App startup | 2-3 seconds | Loading GUI |
| Track skip | <100ms | Fast response |
| UI responsiveness | Smooth | No lag with Pi 4 |
| Image loading | <1 second | Background image |
| Bluetooth pairing | 5-10 seconds | One-time setup |

---

## 🛠️ TOOLS NEEDED FOR BUILD

- Soldering iron (if custom wiring) - $15
- Solder + flux - $5
- Wire strippers - $3
- Screwdriver set - $5
- Breadboard - $2

**OR just use:** Jumper wires + breadboard (no soldering needed!)

---

## 📝 FILE STRUCTURE ON PI

```
/home/pi/MP3-GUI/
├── main.py                 # Main app
├── battery.py             # Battery monitor
├── background.png         # UI background
├── click.ogg              # UI sounds (optional)
├── scroll.wav
├── shutdown.wav
├── requirements.txt
└── tracks/                # Your MP3 files
    ├── song1.mp3
    ├── song2.mp3
    └── ...
```

---

## 💡 TIPS & OPTIMIZATIONS

1. **Disable desktop GUI** on Pi if using Lite: Saves RAM
2. **Use SSD instead of HDD** for faster boot: Optional but better
3. **Enable GPU memory split**: Already optimized on Pi 4
4. **Reduce display brightness** at night: Saves power
5. **Use high-speed MicroSD** (V30): Faster app load
6. **Heatsinks on CPU/RAM**: Prevents thermal throttling
7. **Keep MP3s on fast storage**: SSD via USB if >1000 songs

---

## 🎯 TOTAL PROJECT COST

**Minimum Build:** $145
- Pi 4 (2GB) + 7" Display + Storage + PSU + Case

**With Buttons:** $157
- Add 5x buttons + resistors + wires

**With Better Audio:** $185
- Add USB DAC for higher quality

**Premium Build:** $220
- Pi 4 + Display + Buttons + DAC + Battery UPS

---

## 📚 USEFUL LINKS

- Pi OS Download: https://www.raspberrypi.com/software/
- GPIO Pinout: https://pinout.xyz/
- Display drivers: https://www.waveshare.com/
- Pygame docs: https://www.pygame.org/docs/

---

**Ready to build? Let me know if you need help with GPIO button code or any optimizations!**
