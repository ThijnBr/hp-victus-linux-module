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

- **Victus by HP Gaming Laptop 16** (e.g. `16-r0xxx` / motherboard `8BBE`, `16-s1xxx` / `8C9C`, and other 15/16 models)
- **HP Omen Series** (Omen 15, 16, 17, and Transcend models)

Hardware detection automatically enables keyboard backlight support:
- Registers `hp::kbd_backlight` as the master keyboard backlight device (integrated with UPower & KDE Plasma brightness slider).
- Provides individual zone access (`hp-wmi::zone00`..`zone03` / `rgb_zones`) for per-zone color customization and OpenRGB compatibility.

---

## Requirements

- Linux Kernel 6.0+ (Tested up to `7.2.9-2-cachyos`)
- Kernel headers matching your running kernel (`linux-headers`, `linux-cachyos-headers`, etc.)
- `dkms`
- Compiler matching your kernel build (`gcc` or `clang` / `llvm`)

---

## Installation & Setup

### 1. Build and install with DKMS

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
