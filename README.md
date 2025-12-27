# InterStop

A Python script to disable/enable the internal keyboard on ThinkPad X1 Carbon laptops.

## Description

This script allows you to temporarily disable the internal keyboard, which can be useful when using an external keyboard or to prevent accidental key presses. It automatically detects your desktop environment and uses the appropriate method to disable or enable the keyboard.

## Supported Environments

- **Hyprland (Wayland)**: Uses `hyprctl` to disable/enable the device.
- **GNOME (Wayland)**: Requires root access to unbind/bind the driver via sysfs.
- **X11**: Uses `xinput` to disable/enable the device.

## Requirements

- Python 3
- For Hyprland: `hyprctl` command (part of Hyprland installation)
- For GNOME Wayland: Root access (run with `sudo`)
- For X11: `xinput` command (usually available on X11 systems)

## Usage

1. Run the script:
   ```bash
   python3 DisableKeeb.py
   ```

2. Follow the interactive menu:
   - **D**: Disable the internal keyboard
   - **E**: Enable the internal keyboard
   - **C**: Check the current status and diagnostics
   - **Q**: Quit the program

## Warning

- Disabling the internal keyboard may leave you without input if you don't have external devices connected.
- For GNOME Wayland, operations require root privileges, so run with `sudo python3 DisableKeeb.py`.
- This script is designed specifically for ThinkPad X1 Carbon models. It may not work on other laptops.

## Troubleshooting

- If the script fails, run the **C** (Check) option to diagnose issues.
- Ensure you have the necessary commands installed for your environment.
- For Wayland sessions, make sure the correct desktop environment is detected.

## License

This project is provided as-is, without warranty. Use at your own risk.