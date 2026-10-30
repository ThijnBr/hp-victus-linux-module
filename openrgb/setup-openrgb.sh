#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDEV_RULE_SRC="${SCRIPT_DIR}/99-hp-victus-rgb.rules"
UDEV_RULE_DEST="/etc/udev/rules.d/99-hp-victus-rgb.rules"

echo "=== HP Victus Linux Module - OpenRGB Setup ==="

# 1. Install udev rules for unprivileged access
if [ "$EUID" -ne 0 ]; then
    echo "Requesting root privileges to install udev rules..."
    sudo cp "${UDEV_RULE_SRC}" "${UDEV_RULE_DEST}"
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=leds
    sudo udevadm trigger --subsystem-match=platform
else
    cp "${UDEV_RULE_SRC}" "${UDEV_RULE_DEST}"
    udevadm control --reload-rules
    udevadm trigger --subsystem-match=leds
    udevadm trigger --subsystem-match=platform
fi
echo "[OK] Udev rules installed to ${UDEV_RULE_DEST} and reloaded."

# 2. Determine target user home for OpenRGB config
TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME=$(getent passwd "${TARGET_USER}" | cut -d: -f6)
OPENRGB_DIR="${TARGET_HOME}/.config/OpenRGB"
OPENRGB_CONFIG="${OPENRGB_DIR}/OpenRGB.json"

mkdir -p "${OPENRGB_DIR}"

python3 - <<EOF
import json, os

config_path = "${OPENRGB_CONFIG}"
cfg = {}

if os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"Warning: Could not parse existing {config_path}: {e}")

cfg["LinuxLEDDevices"] = {
    "devices": [
        {
            "name": "HP Victus Keyboard (All Zones)",
            "rgb_path": "/sys/class/leds/hp::kbd_backlight/"
        },
        {
            "name": "HP Victus Zone 1 (Left)",
            "rgb_path": "/sys/class/leds/hp-wmi::zone00/"
        },
        {
            "name": "HP Victus Zone 2 (Center-Left)",
            "rgb_path": "/sys/class/leds/hp-wmi::zone01/"
        },
        {
            "name": "HP Victus Zone 3 (Center-Right)",
            "rgb_path": "/sys/class/leds/hp-wmi::zone02/"
        },
        {
            "name": "HP Victus Zone 4 (Right)",
            "rgb_path": "/sys/class/leds/hp-wmi::zone03/"
        }
    ]
}

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=4)

print(f"[OK] Successfully configured OpenRGB devices in {config_path}")
EOF

# Ensure proper ownership if run as root
if [ -n "${SUDO_USER}" ]; then
    chown -R "${TARGET_USER}:$(id -gn "${TARGET_USER}")" "${OPENRGB_DIR}"
fi

echo ""
echo "OpenRGB setup complete! You can now start OpenRGB:"
echo "  openrgb"
echo "Or list devices via CLI:"
echo "  openrgb --noautoconnect -l"
