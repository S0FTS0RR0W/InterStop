# python program that disables internal keyboard on Thinkpad X1 Carbon

import subprocess
import os
import re

def check_command(command):
    """Check if a command is available in PATH."""
    return subprocess.run(["which", command], capture_output=True).returncode == 0

def disable_hyprland():
    # Hyprland specific: uses hyprctl to disable the device
    if not check_command("hyprctl"):
        print("Error: hyprctl command not found. Is Hyprland installed?")
        return
    
    device_name = "at-translated-set-2-keyboard"
    print(f"Detected Hyprland. Disabling {device_name}...")
    try:
        subprocess.run(["hyprctl", "keyword", f"device:{device_name}:enabled", "false"], check=True)
        print("Internal keyboard disabled via Hyprland.")
    except subprocess.CalledProcessError as e:
        print(f"Error running hyprctl: {e}")

def enable_hyprland():
    # Hyprland specific: uses hyprctl to enable the device
    if not check_command("hyprctl"):
        print("Error: hyprctl command not found. Is Hyprland installed?")
        return
    
    device_name = "at-translated-set-2-keyboard"
    print(f"Detected Hyprland. Enabling {device_name}...")
    try:
        subprocess.run(["hyprctl", "keyword", f"device:{device_name}:enabled", "true"], check=True)
        print("Internal keyboard enabled via Hyprland.")
    except subprocess.CalledProcessError as e:
        print(f"Error running hyprctl: {e}")

def disable_gnome_wayland():
    # GNOME Wayland specific: requires root to unbind driver via sysfs
    if os.geteuid() != 0:
        print("WARNING: Disabling internal keyboard on GNOME Wayland requires root (sudo).")
        print("Please run: sudo python3 DisableKeeb.py")
        return

    print("Detected GNOME Wayland. Attempting to unbind driver via sysfs...")
    try:
        # Find the serio device for the AT keyboard using regex for robustness
        serio_id = None
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()
            # Look for the block containing the keyboard
            blocks = content.split("\n\n")
            for block in blocks:
                if "AT Translated Set 2 keyboard" in block:
                    # Use regex to find Phys= line
                    phys_match = re.search(r'Phys=(.+)', block)
                    if phys_match:
                        phys = phys_match.group(1)
                        # Extract serio part, e.g., serio0 from isa0060/serio0/input0
                        serio_match = re.search(r'(serio\d+)', phys)
                        if serio_match:
                            serio_id = serio_match.group(1)
                            break
        
        if serio_id:
            unbind_path = "/sys/bus/serio/drivers/atkbd/unbind"
            bind_path = "/sys/bus/serio/drivers/atkbd/bind"
            device_path = f"/sys/bus/serio/drivers/atkbd/{serio_id}"
            # Check if device is currently bound
            if os.path.exists(device_path):
                with open(unbind_path, "w") as f:
                    f.write(serio_id)
                print(f"Internal keyboard ({serio_id}) disabled.")
                # Store serio_id for potential re-enable (simple approach: print it)
                print(f"Note: To re-enable, you can manually bind {serio_id} to {bind_path}")
            else:
                print(f"Internal keyboard ({serio_id}) is already disabled.")
        else:
            print("Could not find internal keyboard in /proc/bus/input/devices")
    except Exception as e:
        print(f"Error disabling via sysfs: {e}")

def enable_gnome_wayland():
    # GNOME Wayland specific: requires root to bind driver via sysfs
    if os.geteuid() != 0:
        print("WARNING: Enabling internal keyboard on GNOME Wayland requires root (sudo).")
        print("Please run: sudo python3 DisableKeeb.py")
        return

    print("Detected GNOME Wayland. Attempting to bind driver via sysfs...")
    try:
        # Find the serio device for the AT keyboard (similar to disable)
        serio_id = None
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()
            blocks = content.split("\n\n")
            for block in blocks:
                if "AT Translated Set 2 keyboard" in block:
                    phys_match = re.search(r'Phys=(.+)', block)
                    if phys_match:
                        phys = phys_match.group(1)
                        serio_match = re.search(r'(serio\d+)', phys)
                        if serio_match:
                            serio_id = serio_match.group(1)
                            break
        
        if serio_id:
            bind_path = "/sys/bus/serio/drivers/atkbd/bind"
            device_path = f"/sys/bus/serio/drivers/atkbd/{serio_id}"
            # Check if device is currently unbound
            if not os.path.exists(device_path):
                with open(bind_path, "w") as f:
                    f.write(serio_id)
                print(f"Internal keyboard ({serio_id}) enabled.")
            else:
                print(f"Internal keyboard ({serio_id}) is already enabled.")
        else:
            print("Could not find internal keyboard in /proc/bus/input/devices")
    except Exception as e:
        print(f"Error enabling via sysfs: {e}")

def detectInternalKeyboard():
    if not check_command("xinput"):
        print("Error: xinput command not found. Required for X11.")
        return None
    
    try:
        output = subprocess.check_output(["xinput", "list"], text=True)
        keyboard_lines = [line for line in output.split('\n') if "keyboard" in line.lower() and "AT Translated Set 2 keyboard" in line]

        if keyboard_lines:
            for line in keyboard_lines:
                parts = line.split('id=')
                if len(parts) > 1:
                    return int(parts[1].split()[0])
        return None
    except Exception as e:
        print(f"Error detecting internal keyboard: {e}")
        return None

def disableInternalKeyboard(device_id):
    try:
        subprocess.run(["xinput", "disable", str(device_id)], check=True)
        print(f"Internal keyboard (ID: {device_id}) disabled.")
    except Exception as e:
        print(f"Error disabling keyboard: {e}")

def enableInternalKeyboard(device_id):
    try:
        subprocess.run(["xinput", "enable", str(device_id)], check=True)
        print(f"Internal keyboard (ID: {device_id}) enabled.")
    except Exception as e:
        print(f"Error enabling keyboard: {e}")

def check_keyboard_status():
    print("\n--- Diagnostic Check ---")
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    print(f"Detected Session: {session_type}")
    print(f"Detected Desktop: {desktop}")

    if "wayland" in session_type:
        if "hyprland" in desktop:
            if not check_command("hyprctl"):
                print("FAILURE: 'hyprctl' command not found.")
                return
            print("Checking Hyprland devices...")
            try:
                output = subprocess.check_output(["hyprctl", "devices"], text=True)
                if "at-translated-set-2-keyboard" in output:
                    print("SUCCESS: 'at-translated-set-2-keyboard' found in Hyprland.")
                else:
                    print("FAILURE: 'at-translated-set-2-keyboard' NOT found. Check 'hyprctl devices'.")
            except Exception as e:
                print(f"Error: {e}")
        elif "gnome" in desktop:
            print("Checking /proc/bus/input/devices for GNOME...")
            try:
                with open("/proc/bus/input/devices", "r") as f:
                    content = f.read()
                    if "AT Translated Set 2 keyboard" in content:
                        print("SUCCESS: Internal keyboard detected in system files.")
                        if os.geteuid() != 0:
                            print("NOTE: You are not root. Disabling will fail unless you run with sudo.")
                    else:
                        print("FAILURE: Internal keyboard string not found in /proc/bus/input/devices.")
            except Exception as e:
                print(f"Error reading system files: {e}")
        else:
            print(f"WARNING: Unknown Wayland compositor: {desktop}")
    else:
        print("Checking X11 devices...")
        device_id = detectInternalKeyboard()
        if device_id:
            print(f"SUCCESS: Found X11 device ID: {device_id}")
        else:
            print("FAILURE: X11 device not found.")
    print("------------------------\n")

# Disable on exit
def run_disable_logic():
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    if "wayland" in session_type:
        if "hyprland" in desktop:
            disable_hyprland()
        elif "gnome" in desktop:
            disable_gnome_wayland()
        else:
            print(f"Wayland session detected ({desktop}), but no specific handler found.")
    else:
        # X11 / Default
        device_id = detectInternalKeyboard()
        if device_id:
            print(f"Found ThinkPad X1 Carbon keyboard (ID: {device_id})")
            disableInternalKeyboard(device_id)
        else:
            print("Internal keyboard not found.")

def run_enable_logic():
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    if "wayland" in session_type:
        if "hyprland" in desktop:
            enable_hyprland()
        elif "gnome" in desktop:
            enable_gnome_wayland()
        else:
            print(f"Wayland session detected ({desktop}), but no specific handler found.")
    else:
        # X11 / Default
        device_id = detectInternalKeyboard()
        if device_id:
            print(f"Found ThinkPad X1 Carbon keyboard (ID: {device_id})")
            enableInternalKeyboard(device_id)
        else:
            print("Internal keyboard not found.")

if __name__ == "__main__":
    while True:
        choice = input("\nEnter command (D=Disable, E=Enable, C=Check, Q=Quit): ").strip().upper()
        if choice == 'D':
            run_disable_logic()
        elif choice == 'E':
            run_enable_logic()
        elif choice == 'C':
            check_keyboard_status()
        elif choice == 'Q':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter D, E, C, or Q.")