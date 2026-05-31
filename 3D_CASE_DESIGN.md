# Pocket MP3 Player - 3D Printed Case Design

## Case Specifications

### Outer Dimensions
- **Length:** 120mm
- **Width:** 80mm  
- **Height:** 25mm
- **Wall thickness:** 2mm
- **Material:** PLA or PETG (easiest to print)

### Components to Fit
```
Top section (buttons & OLED):
├── 5x Push buttons (spaced around edge)
└── 2.42" OLED display (centered front)

Middle section (electronics):
├── Raspberry Pi Zero W 2
├── Power bank connection
└── Micro USB power

Bottom section (battery):
└── 5000mAh portable battery
```

## Design Layout

```
      [UP BUTTON]
         ↓
[PREV]  [OLED]  [NEXT]
         ↓
[VOL-] [PLAY] [VOL+]


Inside:
┌─────────────────────┐
│    Buttons (5x)     │  Top section
├─────────────────────┤
│   Pi Zero W 2       │  Middle
│   + USB hub         │  
├─────────────────────┤
│  5000mAh Battery    │  Bottom section
└─────────────────────┘
```

## 3D Printing Options

### Option A: Download & Modify Existing
1. Go to **Thingiverse.com**
2. Search: "Raspberry Pi Zero case"
3. Download one that fits these dims:
   - https://www.thingiverse.com/thing:4694624
   - https://www.thingiverse.com/thing:3754665
4. Modify STL file using **Fusion 360** (free) or **Blender** (free)
5. Add button holes using CAD software

### Option B: Commission Design
- **Fiverr:** $15-30 for custom STL design
- Search: "Design Raspberry Pi Zero case STL"
- Describe dimensions + button placement
- Download + print

### Option C: Simple 3D Model (DIY)
Create using **OpenSCAD** (free, parametric):

```openscad
// Simple enclosure
$fn = 32;

// Outer box
difference() {
    cube([120, 80, 25], center=true);
    // Hollow inside
    translate([0, 0, 2])
    cube([116, 76, 22], center=true);
}

// Button holes (top face)
for (angle = [0, 72, 144, 216, 288]) {
    rotate([0, 0, angle])
    translate([30, 0, 13])
    cylinder(r=5, h=3, center=true);
}

// OLED window
translate([0, -35, 13])
cube([40, 20, 3], center=true);

// USB port hole
translate([60, 0, 0])
cube([10, 8, 10], center=true);
```

### Print Settings
- **Layer height:** 0.2mm (fast)
- **Infill:** 15% (saves plastic)
- **Support:** Yes (for overhangs)
- **Print time:** 4-6 hours
- **Filament:** ~60g ($1-2)

---

## Printing Services (If No 3D Printer)

| Service | Price | Time | Quality |
|---------|-------|------|---------|
| **Thingiverse prints** | $20-40 | 1-2 weeks | Good |
| **Local maker space** | $5-15 | 1-2 days | Great |
| **Shapeways** | $40-70 | 2-3 weeks | Excellent |
| **3DHubs** | $25-50 | 1 week | Very good |
| **Fiverr printer** | $15-35 | 1-2 weeks | Variable |

---

## Assembly Inside Case

### Layer 1 (Bottom): Battery
```
[5000mAh Power Bank]
├─ Micro USB → Pi
└─ USB-A → NOT USED (power only)
```

### Layer 2 (Middle): Electronics
```
[Raspberry Pi Zero W 2]
├─ GPIO pins facing up
├─ Micro USB power ← Battery
└─ 3.5mm audio jack → Bluetooth dongle or external DAC
```

### Layer 3 (Top): Display & Buttons
```
[2.42" OLED on I2C pins]
├─ VCC → 3.3V
├─ GND → GND
├─ SDA → GPIO 2
└─ SCL → GPIO 3

[5x Push Buttons] soldered to GPIO pins:
├─ Button 1 → GPIO 17 (PLAY)
├─ Button 2 → GPIO 27 (NEXT)
├─ Button 3 → GPIO 22 (PREV)
├─ Button 4 → GPIO 23 (VOL+)
└─ Button 5 → GPIO 24 (VOL-)
```

---

## Wiring Diagram (Inside Case)

```
┌──────────────────────────────────┐
│     OLED Display (I2C)           │
│  VCC SDA SCL GND                 │
│   │   │   │   │                  │
│   │   │   │   └─────┐            │
│   │   │   └───┐     │            │
│   │   └─┐     │     │            │
│   └─┐  │      │     │            │
│     │  │      │     │            │
│ ┌───┴──┴──────┴─────┴─┐          │
│ │  Pi Zero W 2       │          │
│ │ [Button pins GPIO] │          │
│ │   3.5V  SDA SCL GND│          │
│ └───┬──┬──────┬─────┬─┘          │
│     │  │      │     │            │
│     │  │      │     │            │
│ [Push buttons x5 + resistors]    │
│     │  │      │     │            │
│     └──┴──────┴─────┘            │
│            │                     │
│     [Micro USB Power]            │
│            │                     │
│    [5000mAh Battery]             │
└──────────────────────────────────┘
```

---

## Mounting Strategy

### Buttons: PCB-mounted
```
Option A: Through-hole soldering
- Solder buttons directly to GPIO header
- Mount on PCB bracket inside case

Option B: Breadboard temporary
- Use small breadboard
- Test before permanent assembly
- Easier to modify
```

### Display: Standoff-mounted
```
Use small M2 brass standoffs:
- 15mm height (for clearance)
- Mount OLED on top face
- Leaves room for buttons around it
```

### Battery: Double-sided tape
```
- Stick 5000mAh battery on bottom face
- Wrap in foam padding
- Glue Pi Zero W 2 next to it
```

---

## Alternative: Buy Pre-made Case

If 3D printing too complex:
- Search Amazon: "Raspberry Pi Zero W case"
- Modify with drill/Dremel
- Add button holes manually (~$10 + case)

---

## Testing Before Final Assembly

1. **Print case frame first** (support walls only)
2. **Test fit all components** (loose assembly)
3. **Verify GPIO connections** (all buttons work)
4. **Check OLED display** (visible through window)
5. **Test audio output** (headphone jack accessible)
6. **Adjust holes/windows** if needed
7. **Print final case** (with refinements)
8. **Permanent assembly** (glue/solder)

---

## File Requirements for 3D Printer

Save STL file then:

### Using Cura (free slicer):
1. Download **Ultimaker Cura** (free)
2. Open STL file
3. Orient model
4. Slice (generates G-code)
5. Export to printer

### Print command (if direct):
```bash
# Linux/Mac
lp -d printer_name model.stl

# Raspberry Pi connected to printer:
lp -h printer_ip model.stl
```

---

## Cost Summary

| Item | Cost |
|------|------|
| 3D printed case (DIY) | $2-5 |
| 3D printed case (service) | $20-40 |
| Brass standoffs/hardware | $2 |
| Buttons (5x) + resistors | $3 |
| Wiring + solder | $2 |
| **Total add-on cost** | $9-50 |

---

**Ready to print? Use any of the Thingiverse designs or commission a custom one!**
