# Circuit Schematic

## Wokwi / Tinkercad Link

> Add your schematic link here after creating it.

**Example URL format:**
- Wokwi: `https://wokwi.com/projects/<your-project-id>`
- Tinkercad: `https://www.tinkercad.com/things/<your-thing-id>`

---

## Schematic Description

One representative room is wired (Drawing Room: 2 fans + 3 lights).

**Components used:**
- ESP32 microcontroller
- Relay modules (one per device) for on/off control
- LED(s) representing lights
- DC motor(s) or fan symbols for fans
- (Optional) ACS712 current sensor on main line for current sensing

**Concept:**
The ESP32 reads device states from the backend (via Wi-Fi HTTP call) and drives relay outputs to physically toggle devices. The ACS712 sensor optionally measures current draw and reports back.
