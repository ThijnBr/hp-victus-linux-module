# HP Victus & Omen Linux Kernel Module (hp-wmi)

Upstream-oriented Linux kernel platform driver for HP Victus and HP Omen laptops, providing native integration with **KDE Plasma's keyboard backlight brightness slider**, UPower, standard Linux multicolor LED subsystem, platform profiles, and fan monitoring.

## Features

- **KDE Plasma & UPower Integration:**
  - Directly drives KDE Plasma's built-in keyboard backlight slider and battery/brightness plasmoid via `org.freedesktop.UPower.KbdBacklight`.
  - Exposes standard sysfs LED class devices (`hp::kbd_backlight` for single-zone RGB models and `hp::kbd_zoned_backlight-[left|middle|right|wasd]` for 4-zone models).
  - Handles hardware backlight hotkey events (Fn+F4 / backlight toggle) and reports them to userspace using the kernel LED subsystem (`brightness_hw_changed`), ensuring KDE's slider stays in sync in real time.
- **Multicolor LED Subsystem:**
  - Standard `multi_intensity` (RGB channels 0–255) and `brightness` attributes per `Documentation/leds/leds-class.rst`.
  - Preserves selected color when adjusting brightness or dimming.
  - Safe default: defaults to white on cold boot if uninitialized, preventing dark keyboard issues on first slider drag.
- **Thermal Profiles & Fan Monitoring:**
  - ACPI / WMI platform profile integration (`performance`, `balanced`, `quiet`, `cool`).
  - Standard Linux `hwmon` fan speed reporting.
- **Automated Kernel & Compiler Compatibility:**
  - Compatible with modern kernels (Linux 6.x and 7.x).
  - Automatically detects whether the running kernel was built with Clang/LLVM (e.g. CachyOS) or GCC, exporting `CC=clang LLVM=1` seamlessly for both local builds and DKMS.

---

## Hardware Support

- **Victus by HP Gaming Laptop 15 & 16** (e.g. `16-r0xxx` / motherboard `8BBE`, `16-s1xxx` / `8C9C`, and other 15/16 models)
  - Physically equipped with a **single-zone RGB** backlit keyboard.
  - Automatically configured with a unified keyboard backlight (`hp::kbd_backlight` and `hp-wmi::zone00`), avoiding non-functioning phantom zones.
- **HP Omen Series** (Omen 15, 16, 17, and Transcend models)
  - Equipped with **4-zone RGB** keyboards.
  - Automatically configured with all 4 independent zones (`hp-wmi::zone00`..`zone03`).

### Module Parameters

You can inspect or override the zone detection behavior using the `single_zone` parameter:

```bash
# Force single-zone mode (default for HP Victus)
sudo modprobe hp_wmi single_zone=1

# Force 4-zone mode (default for HP Omen)
sudo modprobe hp_wmi single_zone=0

# Auto-detect based on DMI / laptop model (default: single_zone=-1)
sudo modprobe hp_wmi single_zone=-1
```

To make an override permanent across reboots, add to `/etc/modprobe.d/hp-wmi.conf`:
```
options hp_wmi single_zone=1
```

---

## Requirements

- Linux Kernel 6.0+ (Tested up to `7.2.9-2-cachyos`)
- Kernel headers matching your running kernel (`linux-headers`, `linux-cachyos-headers`, etc.)
- `dkms`
- Compiler matching your kernel build (`gcc` or `clang` / `llvm`)

---

## Installation & Setup

### Option A: Arch Linux / CachyOS (AUR)

You can install the package directly via your AUR helper:

```bash
paru -S hp-victus-wmi-dkms-git
# or
yay -S hp-victus-wmi-dkms-git
```

### Option B: Build and install with DKMS manually

To ensure the driver persists across kernel updates:

```bash
# Clone the repository
git clone https://github.com/ThijnBr/hp-victus-linux-module.git
cd hp-victus-linux-module

# Install into DKMS (automatically builds and installs for the active kernel)
sudo make install
```

### 2. Load the Module

Reload the module immediately:

```bash
# Unload in-tree driver and load custom module
sudo make unload
sudo make load

# Or manually:
sudo modprobe -r hp_wmi
sudo modprobe hp_wmi
```

### 3. Verify KDE Plasma Integration

Once loaded:
1. Confirm the LED device exists:
   ```bash
   ls -d /sys/class/leds/hp::kbd*
   ```
2. Confirm UPower detects the keyboard backlight:
   ```bash
   busctl introspect org.freedesktop.UPower /org/freedesktop/UPower/KbdBacklight
   ```
3. Open KDE Plasma's System Tray -> **Brightness and Color** / **Battery and Brightness**. The **Keyboard Backlight** slider will be visible and operational.

---

## Usage & Controls

### KDE Plasma Slider
Use the native slider in the System Tray or keyboard shortcut settings.

### Command Line Control

- **Set Brightness (0–255):**
  ```bash
  echo 180 | sudo tee /sys/class/leds/hp::kbd_backlight/brightness
  ```

- **Set RGB Color (`multi_intensity`):**
  ```bash
  # Pure Red
  echo "255 0 0" | sudo tee /sys/class/leds/hp::kbd_backlight/multi_intensity

  # Pure Cyan
  echo "0 255 255" | sudo tee /sys/class/leds/hp::kbd_backlight/multi_intensity

  # Pure White
  echo "255 255 255" | sudo tee /sys/class/leds/hp::kbd_backlight/multi_intensity
  ```

- **Via DBus (same path used by KDE PowerDevil):**
  ```bash
  busctl --user call org.kde.Solid.PowerManagement \
    /org/kde/Solid/PowerManagement/Actions/KeyboardBrightnessControl \
    org.kde.Solid.PowerManagement.Actions.KeyboardBrightnessControl \
    setKeyboardBrightness i 200
  ```

### Python GUI

A lightweight graphical controller is included in the repository:

```bash
sudo ./hp_victus_rgb_gui.py
```

---

## OpenRGB Integration

The module is fully compatible with [OpenRGB](https://openrgb.org) using its native `LinuxLEDController` subsystem. Both single-zone RGB (HP Victus) and 4-zone RGB (HP Omen) configurations are supported without requiring OpenRGB to run as root.

### 1. Automated OpenRGB Setup

Run the included setup script:

```bash
# Auto-detects zones (defaults to single-zone for Victus):
./openrgb/setup-openrgb.sh

# Or explicitly force mode:
./openrgb/setup-openrgb.sh --single-zone   # 1 unified zone
./openrgb/setup-openrgb.sh --four-zone     # 4 individual zones (HP Omen)
```

This script:
1. Installs the udev rule (`/etc/udev/rules.d/99-hp-victus-rgb.rules`) so normal users have read/write access to the sysfs LED and RGB attributes without sudo.
2. Configures `~/.config/OpenRGB/OpenRGB.json` with the matching keyboard device(s).

### 2. Manual Configuration

If configuring manually, add the following to `~/.config/OpenRGB/OpenRGB.json`:

**For Single-Zone Models (HP Victus):**
```json
{
    "LinuxLEDDevices": {
        "devices": [
            {
                "name": "HP Victus Keyboard Backlight",
                "rgb_path": "/sys/class/leds/hp::kbd_backlight/"
            }
        ]
    }
}
```

**For 4-Zone Models (HP Omen):**
```json
{
    "LinuxLEDDevices": {
        "devices": [
            {
                "name": "HP Omen Keyboard Backlight (All Zones)",
                "rgb_path": "/sys/class/leds/hp::kbd_backlight/"
            },
            {
                "name": "HP Omen Zone 1 (Left)",
                "rgb_path": "/sys/class/leds/hp-wmi::zone00/"
            },
            {
                "name": "HP Omen Zone 2 (Center-Left)",
                "rgb_path": "/sys/class/leds/hp-wmi::zone01/"
            },
            {
                "name": "HP Omen Zone 3 (Center-Right)",
                "rgb_path": "/sys/class/leds/hp-wmi::zone02/"
            },
            {
                "name": "HP Omen Zone 4 (Right)",
                "rgb_path": "/sys/class/leds/hp-wmi::zone03/"
            }
        ]
    }
}
```

### 3. OpenRGB CLI Examples

List detected devices:
```bash
openrgb --noautoconnect -l
```

Set color on HP Victus (single zone):
```bash
openrgb --noautoconnect --device "HP Victus Keyboard Backlight" --color 00FFFF
```

Set color on HP Omen:
```bash
openrgb --noautoconnect \
  --device "HP Omen Zone 1 (Left)" --color FF0000 \
  --device "HP Omen Zone 2 (Center-Left)" --color 00FF00 \
  --device "HP Omen Zone 3 (Center-Right)" --color 0000FF \
  --device "HP Omen Zone 4 (Right)" --color FFFF00
```


---

## Uninstallation

To remove the module and restore the default in-tree driver:

```bash
sudo make uninstall
sudo modprobe -r hp_wmi
sudo modprobe hp_wmi
```

---

## License

GPL-2.0
