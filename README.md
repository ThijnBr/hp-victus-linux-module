HP Omen and Victus special feature control for Linux
----------------------------------------------------

This repository is a fork of `pelrun/hp-omen-linux-module` adapted to build and run on Arch Linux kernel 6.17.6-arch1-1. Upstream project: [pelrun/hp-omen-linux-module](https://github.com/pelrun/hp-omen-linux-module).

It's experimental and could crash your machine.

**USE AT YOUR OWN RISK**

Currently working:

- FourZone keyboard colour control (`/sys/devices/platform/hp-wmi/rgb_zones/zone0[0-3]`)
  - Supported on HP Victus 16 (and other Victus models with RGB keyboard)
## Requirements (Arch Linux)

- dkms
- linux-headers for your running kernel (e.g. `linux-headers` matching 6.17.6-arch1-1)

## Installation

1. Ensure headers are installed for your current kernel: `pacman -S dkms linux-headers`
2. Build and install via DKMS: `sudo make install`

DKMS will rebuild the module automatically on kernel updates.

## Uninstall

`sudo make uninstall`

## Usage

The module creates four files in `/sys/devices/platform/hp-wmi/rgb_zones/` named `zone00 - zone03`.

To change a zone color, write a hex RGB value to the respective file, e.g.:

`sudo bash -c 'echo 00FFFF > /sys/devices/platform/hp-wmi/rgb_zones/zone00'`

Omen and other hotkeys are bound to regular X11 keysyms. Use your desktop's hotkey manager to map them.

### Optional GUI for Victus

`hp_victus_rgb_gui.py` provides a simple GUI for changing Victus RGB zones.

